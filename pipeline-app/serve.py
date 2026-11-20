"""
Canary Lab with live runs.

    python pipeline-app/serve.py              # opens http://127.0.0.1:8765 in the browser
    python pipeline-app/serve.py --no-browser --port 8765

The published page can only replay recorded answers: it has no API keys and must never
hold any. This server runs on your own computer instead. It serves the same page with
the current results from the project files, and lets the Run button record new runs:
the attacker model writes the prompts (Claude through Claude Code by default), Gemini
answers through the API, the rule check scores the reply and the LLM judges grade it.
New runs are saved to responses_generated.jsonl and judgments_generated.jsonl, the same
files the command line uses, so the reports and drift charts include them.

Safety: the server listens on 127.0.0.1 only and the keys stay in this process. The page
gets a random token, and the API refuses requests without it or with another host name,
so other websites open in the browser cannot start runs. One run happens at a time.
"""

import argparse
import json
import re
import secrets
import socket
import sys
import threading
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

APP = Path(__file__).resolve().parent
ROOT = APP.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(APP))

import drift  # noqa: E402
import embed_data  # noqa: E402
import goals  # noqa: E402
import llm_judge  # noqa: E402
import run_targets  # noqa: E402
from datalab.lab import DataLab  # noqa: E402
from env_keys import load_saved_keys  # noqa: E402

DATA_PAIRS = [
    ("sample_responses.jsonl", "judgments.jsonl"),
    ("responses_l4.jsonl", "judgments_l4.jsonl"),
    ("responses_generated.jsonl", "judgments_generated.jsonl"),
]
LIVE_RESPONSES = ROOT / "responses_generated.jsonl"
LIVE_JUDGMENTS = ROOT / "judgments_generated.jsonl"
DEFAULT_ATTACKER = "claude_code:claude-opus-5-5"
MODEL_ID = re.compile(r"^gemini-[a-z0-9][a-z0-9.\-]{0,60}$")
MAX_BODY = 4096
LINGER_SECONDS = 2.0  # after an answer, how long to keep reading what the client still sends
LINGER_BYTES = 64 * 1024  # and how much of it at most


def short(error, limit=220):
    text = " ".join(str(error).split())
    return text if len(text) <= limit else text[:limit] + "..."


# ── Data for the page ─────────────────────────────────────────────────

def current_data():
    """Dataset and drift observations built from the project files right now."""
    exports, response_files, judgment_files = [], [], []
    for responses, judgments in DATA_PAIRS:
        rp, jp = ROOT / responses, ROOT / judgments
        if not rp.exists():
            continue
        rows, judges = llm_judge.collect(llm_judge.load_jsonl(rp), llm_judge.load_records(jp))
        exports.append({"judges": judges, "items": llm_judge.app_items(rows)})
        response_files.append(rp)
        if jp.exists():
            judgment_files.append(jp)
    dataset = embed_data.merge_exports(exports, "project files (live)")
    series, models = drift.observations(response_files, judgment_files)
    drift_data = {"params": dict(drift.DEFAULTS), "reference": "auto",
                  "judges": {jid: {"model": models.get(jid, ""), "observations": obs} for jid, obs in series.items()}}
    return dataset, drift_data


def page_html(token):
    dataset, drift_data = current_data()
    page = embed_data.inject((APP / "index.html").read_text(encoding="utf-8"),
                             embed_data.build_payload(llm_judge, dataset, drift_data))
    live = {"token": token, "attacker": DEFAULT_ATTACKER, "out": LIVE_RESPONSES.name}
    tag = "<script>window.CANARY_LAB_LIVE = " + json.dumps(live).replace("<", "\\u003c") + ";</script>\n"
    anchor = '<script type="application/json" id="embedded-data">'
    if anchor not in page:
        raise ValueError("the page has no embedded-data script tag")
    return page.replace(anchor, tag + anchor, 1)  # before the page script, which reads it on start


# ── Runs ──────────────────────────────────────────────────────────────

class Lab:
    def __init__(self, token):
        self.token = token
        self.jobs = {}
        self.busy = threading.Lock()
        self.datalab = DataLab(ROOT)  # the Data structures section; it has its own lock


def validate_request(body):
    scenarios = {s["id"]: s for s in run_targets.load_jsonl(ROOT / "attacks.jsonl")}
    goal = body.get("goal", "canary")
    picked = body.get("scenarios") or []
    model = str(body.get("model", ""))
    runs, turns = body.get("runs", 1), body.get("turns", 3)
    if goal not in goals.GOALS:
        raise ValueError(f"unknown goal {goal!r}")
    if not (isinstance(picked, list) and 1 <= len(picked) <= 3 and all(p in scenarios for p in picked)):
        raise ValueError("pick one to three known attack scenarios")
    if len(set(picked)) != len(picked):
        raise ValueError("each scenario can be used once")
    if not MODEL_ID.match(model):
        raise ValueError(f"not a Gemini model id: {model!r}")
    if not (isinstance(runs, int) and 1 <= runs <= 5 and isinstance(turns, int) and 1 <= turns <= 5):
        raise ValueError("runs and turns must be whole numbers from 1 to 5")
    return SimpleNamespace(goal=goal, combo=[scenarios[p] for p in picked], model=model, runs=runs, turns=turns)


def run_job(lab, job, req):
    log = job["log"].append
    try:
        load_saved_keys()
        spec = goals.GOALS[req.goal]
        attack_id = run_targets.attack_id_for(req.goal, req.combo)
        saved = run_targets.load_jsonl(LIVE_RESPONSES) if LIVE_RESPONSES.exists() else []
        previous = [r["run"] for r in saved
                    if r.get("model") == req.model and r.get("attack_id") == attack_id and r.get("condition") == spec["tag"]]
        args = SimpleNamespace(
            goal=req.goal, scenario="+".join(sc["id"] for sc in req.combo), models=req.model,
            runs=max(previous, default=0) + req.runs, turns=req.turns, attacker=DEFAULT_ATTACKER, knowledge="none",
            attacks=str(ROOT / "attacks.jsonl"), code_execution=False, temperature=None, system=None, tag=None,
            delay=0, out=str(LIVE_RESPONSES), progress=log)
        log(f"Recording {req.runs} new run(s) of {' + '.join(sc['technique'] for sc in req.combo)} on {req.model}.")
        rows = run_targets.cmd_generate(args, log=log)
        if not rows:
            raise RuntimeError("no run was saved, see the messages above")

        for judge in llm_judge.load_judges(ROOT / "judges.json", None):
            try:
                call = llm_judge.make_caller(judge)
            except llm_judge.JudgeUnavailable as error:
                log(f"{judge['id']} judge skipped: {error}")
                continue
            for row in rows:
                log(f"{judge['id']} judge ({judge['model']}) is grading run {row['run']}")
                try:
                    record = llm_judge.grade_one(
                        judge, call, row, on_retry=lambda *wait: log(llm_judge.retry_message(f"{judge['id']} judge", *wait)))
                except Exception as error:
                    log(f"{judge['id']} judge skipped: {short(error)}")
                    break
                with open(LIVE_JUDGMENTS, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                log(f"{judge['id']} judge: " + (record.get("error") or f"level {record['level']}"))

        graded, judges = llm_judge.collect(rows, llm_judge.load_records(LIVE_JUDGMENTS))
        _, drift_data = current_data()
        job.update(state="done", items=llm_judge.app_items(graded), judges=judges, drift=drift_data)
        log("Done. The new run is saved and shown below.")
    except BaseException as error:  # SystemExit from the runner counts as a failure too
        if not isinstance(error, (RuntimeError, SystemExit, ValueError)):
            traceback.print_exc()
        job.update(state="failed", error=short(error, 400))
        log(f"Stopped: {short(error, 400)}")
    finally:
        lab.busy.release()


# ── HTTP ──────────────────────────────────────────────────────────────

def make_handler(lab, port):
    hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    origins = {f"http://{h}" for h in hosts}

    class Handler(BaseHTTPRequestHandler):
        server_version = "CanaryLab/1"

        def log_message(self, fmt, *args):  # keep the terminal quiet
            pass

        def finish(self):
            super().finish()
            self.linger()

        def linger(self):
            """Lingering close (RFC 9112, section 9.6), issue ISS-12.

            Refusals (403, 404, 413, 415) answer without reading the request body. Closing a
            socket that still has unread bytes makes Windows send a reset instead of a normal
            close, and the reset can throw away the answer before the client reads it, so the
            client sees WinError 10053 instead of the refusal. So after the answer: stop sending,
            then read and discard what is left until the client closes, for a short time at most.
            Nothing read here is used, and it happens after the answer is already sent.
            """
            sock = self.connection
            try:
                sock.shutdown(socket.SHUT_WR)
                deadline = time.monotonic() + LINGER_SECONDS
                left = LINGER_BYTES
                while left > 0:
                    wait = deadline - time.monotonic()
                    if wait <= 0:
                        break
                    sock.settimeout(wait)
                    chunk = sock.recv(min(left, 65536))
                    if not chunk:  # the client has closed its side
                        break
                    left -= len(chunk)
            except OSError:  # timeout, or the client is gone already
                pass

        def send_json(self, status, data):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def allowed(self, api):
            # The host check stops DNS rebinding; the token and origin checks stop other sites.
            if self.headers.get("Host") not in hosts:
                self.send_json(403, {"error": "wrong host name"})
                return False
            if api:
                origin = self.headers.get("Origin")
                if origin and origin not in origins:
                    self.send_json(403, {"error": "wrong origin"})
                    return False
                if not secrets.compare_digest(self.headers.get("X-Lab-Token", ""), lab.token):
                    self.send_json(403, {"error": "missing or wrong token, reload the page"})
                    return False
            return True

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                if not self.allowed(False):
                    return
                try:
                    body = page_html(lab.token).encode("utf-8")
                except Exception as error:
                    traceback.print_exc()
                    self.send_json(500, {"error": short(error)})
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            elif path.startswith("/api/job/"):
                if not self.allowed(True):
                    return
                job = lab.jobs.get(path.rsplit("/", 1)[-1])
                if not job:
                    self.send_json(404, {"error": "no such run"})
                    return
                self.send_json(200, {k: job.get(k) for k in ("state", "log", "items", "judges", "drift", "error")})
            else:
                self.send_json(404, {"error": "not found"})

        def do_POST(self):
            if self.path not in ("/api/run", "/api/datalab"):
                self.send_json(404, {"error": "not found"})
                return
            if not self.allowed(True):
                return
            if "application/json" not in self.headers.get("Content-Type", ""):
                self.send_json(415, {"error": "send JSON"})
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY:
                self.send_json(413, {"error": "request too large"})
                return
            if self.path == "/api/datalab":
                # Build, sort or search: quick enough to answer straight away (a few seconds at most).
                try:
                    self.send_json(200, lab.datalab.handle(json.loads(self.rfile.read(length))))
                except (ValueError, TypeError, AttributeError) as error:
                    self.send_json(400, {"error": str(error)})
                except Exception as error:
                    traceback.print_exc()
                    self.send_json(500, {"error": short(error)})
                return
            try:
                req = validate_request(json.loads(self.rfile.read(length)))
            except (ValueError, TypeError, AttributeError) as error:
                self.send_json(400, {"error": str(error)})
                return
            if not lab.busy.acquire(blocking=False):
                self.send_json(409, {"error": "a run is already going, wait for it to finish"})
                return
            job_id = secrets.token_hex(8)
            job = {"state": "running", "log": []}
            lab.jobs[job_id] = job
            threading.Thread(target=run_job, args=(lab, job, req), daemon=True).start()
            self.send_json(202, {"job": job_id})

    return Handler


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Canary Lab with live runs (local only)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser")
    args = parser.parse_args()

    lab = Lab(secrets.token_urlsafe(24))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(lab, args.port))
    except OSError as error:
        sys.exit(f"Could not use port {args.port}: {error}. Close the other server or pass --port.")
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Canary Lab is running at {url}  (Ctrl+C stops it)")
    print("Runs use your saved API keys and are saved to responses_generated.jsonl.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
