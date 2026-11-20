"""
Drift monitoring for the LLM judges with EWMA and CUSUM control charts.

Each judge's grades are put in the order they were made (judgment timestamp). Every grade
becomes one observation:

    x = judge level - reference level

The reference is the hand label when the response has one, otherwise the rule check
(deviation_detector.py for the canary goal, goals.py for the others). x > 0 means the judge
graded stricter than the reference, x < 0 more lenient. A judge that drifts, for example
after a silent model update, shifts the mean of x.

Phase I: the first --baseline grades (at most half of all grades) give the target mean mu0 and the spread sigma0
(sample standard deviation, at least --min-sigma, because levels are whole numbers and a
baseline with no errors has a spread of 0). Phase II: every later grade is monitored.

EWMA    z_t = lam * x_t + (1 - lam) * z_(t-1),  z_0 = mu0
        limits mu0 +- L * sigma0 * sqrt(lam / (2 - lam) * (1 - (1 - lam)^(2t)))
CUSUM   C+_t = max(0, x_t - (mu0 + k*sigma0) + C+_(t-1))
        C-_t = max(0, (mu0 - k*sigma0) - x_t + C-_(t-1))
        alarm when C+ or C- exceeds h * sigma0

A shift says the judge's relation to the reference changed. That can be the judge, or a new
mix of responses (for example many more hint-level cases). To test the judge alone, re-grade a
fixed anchor set, such as the 22 hand-labelled samples, on later days with --repeats 2, 3, ...
and monitor with --reference label.

Usage:
    python drift.py --responses sample_responses.jsonl responses_l4.jsonl responses_generated.jsonl \\
                    --judgments judgments.jsonl judgments_l4.jsonl judgments_generated.jsonl
    python drift.py ... --reference label --judges claude --export app_drift.json
"""

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

DEFAULTS = {"baseline": 20, "lam": 0.2, "L": 3.0, "k": 0.5, "h": 5.0, "min_sigma": 0.5}


# ── Chart math ────────────────────────────────────────────────────────

def baseline(xs, n0, min_sigma):
    """Mean and spread of the first n0 observations, at most half the series so half is left to monitor."""
    n0 = max(2, min(n0, len(xs) // 2))
    base = xs[:n0]
    mu = sum(base) / len(base)
    var = sum((x - mu) ** 2 for x in base) / (len(base) - 1) if len(base) > 1 else 0.0
    return n0, mu, max(math.sqrt(var), min_sigma)


def ewma(xs, mu, sigma, lam, L):
    out, z = [], mu
    for t, x in enumerate(xs, 1):
        z = lam * x + (1 - lam) * z
        width = L * sigma * math.sqrt(lam / (2 - lam) * (1 - (1 - lam) ** (2 * t)))
        out.append({"z": z, "ucl": mu + width, "lcl": mu - width, "alarm": abs(z - mu) > width})
    return out


def cusum(xs, mu, sigma, k, h):
    out, up, down = [], 0.0, 0.0
    K, H = k * sigma, h * sigma
    for x in xs:
        up = max(0.0, x - (mu + K) + up)
        down = max(0.0, (mu - K) - x + down)
        out.append({"up": up, "down": down, "H": H, "alarm_up": up > H, "alarm_down": down > H})
    return out


def first(points, start, test):
    return next((t for t, p in enumerate(points[start:], start + 1) if test(p)), None)


def monitor(xs, params):
    n0, mu, sigma = baseline(xs, params["baseline"], params["min_sigma"])
    e = ewma(xs, mu, sigma, params["lam"], params["L"])
    c = cusum(xs, mu, sigma, params["k"], params["h"])
    return {
        "n0": n0, "mu0": mu, "sigma0": sigma, "ewma": e, "cusum": c,
        # Alarms only count after the baseline (phase II).
        "ewma_alarm": first(e, n0, lambda p: p["alarm"]),
        "cusum_up_alarm": first(c, n0, lambda p: p["alarm_up"]),
        "cusum_down_alarm": first(c, n0, lambda p: p["alarm_down"]),
    }


# ── Reading the data ──────────────────────────────────────────────────

def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_detector():
    spec = importlib.util.spec_from_file_location("deviation_detector", HERE / "deviation_detector.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def item_id(row):
    return str(row["id"]) if row.get("id") else f"s{row.get('session', '?')}-a{row.get('attempt', '?')}"


def observations(response_files, judgment_files, judges=None):
    """Every graded response per judge, in the order the grades were made."""
    detector = load_detector()
    refs = {}
    for path in response_files:
        for row in load_jsonl(path):
            refs[item_id(row)] = {"label": row.get("label"), "rule": detector.score_response(row)["scored_level"],
                                  "goal": row.get("goal") or "canary", "technique": row.get("technique")}
    latest, models = {}, {}
    order = 0
    for path in judgment_files:
        for rec in load_jsonl(path):
            order += 1
            if "level" not in rec or rec["item"] not in refs:
                continue
            if judges and rec["judge"] not in judges:
                continue
            latest[(rec["item"], rec["judge"], rec.get("repeat", 1))] = (rec.get("timestamp", ""), order, rec)
            models[rec["judge"]] = rec.get("model", "")
    series = {}
    for (iid, jid, repeat), (stamp, n, rec) in sorted(latest.items(), key=lambda kv: (kv[1][0], kv[1][1])):
        series.setdefault(jid, []).append({"item": iid, "repeat": repeat, "timestamp": stamp,
                                           "level": rec["level"], **refs[iid]})
    return series, models


def values(obs, reference):
    """x = judge level - reference. Observations without the chosen reference are skipped."""
    xs, kept = [], []
    for o in obs:
        if reference == "label":
            ref = o["label"]
        elif reference == "rule":
            ref = o["rule"]
        else:
            ref = o["label"] if o["label"] is not None else o["rule"]
        if ref is None:
            continue
        xs.append(o["level"] - ref)
        kept.append(o)
    return xs, kept


# ── Report ────────────────────────────────────────────────────────────

def describe(t, kept):
    if t is None:
        return "none"
    o = kept[t - 1]
    return f"grade {t} ({o['item']}, {o['timestamp'][:16].replace('T', ' ')})"


def report(series, models, reference, params):
    print("# Judge drift (EWMA and CUSUM)\n")
    print(f"x = judge level - {'hand label, or the rule check when there is none' if reference == 'auto' else reference}. "
          f"Baseline: first {params['baseline']} grades. EWMA lambda {params['lam']}, limits {params['L']} sigma. "
          f"CUSUM k {params['k']} sigma, h {params['h']} sigma. Sigma is at least {params['min_sigma']}.\n")
    print("| Judge | Grades | Baseline mean | Baseline sigma | Mean after baseline | EWMA alarm | CUSUM stricter | CUSUM more lenient |")
    print("|---|---|---|---|---|---|---|---|")
    results = {}
    for jid, obs in sorted(series.items()):
        xs, kept = values(obs, reference)
        if len(xs) < 4:
            print(f"| {jid} ({models.get(jid, '')}) | {len(xs)} | too few grades to monitor | | | | | |")
            continue
        m = monitor(xs, params)
        after = xs[m["n0"]:]
        mean_after = f"{sum(after) / len(after):+.2f}" if after else "-"
        print(f"| {jid} ({models.get(jid, '')}) | {len(xs)} | {m['mu0']:+.2f} | {m['sigma0']:.2f} | {mean_after} | "
              f"{describe(m['ewma_alarm'], kept)} | {describe(m['cusum_up_alarm'], kept)} | {describe(m['cusum_down_alarm'], kept)} |")
        results[jid] = (m, kept)
    print("\nAn alarm means the judge's grades moved away from the baseline relation to the reference. "
          "Check the responses around the alarm: a new kind of response can cause it as well as a changed judge.")
    return results


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="EWMA and CUSUM drift charts for the LLM judges")
    parser.add_argument("--responses", nargs="+", required=True, help="Responses JSONL files that were judged")
    parser.add_argument("--judgments", nargs="+", required=True, help="Judgments JSONL files from llm_judge.py")
    parser.add_argument("--judges", help="Comma-separated judge ids (default all)")
    parser.add_argument("--reference", choices=("auto", "label", "rule"), default="auto",
                        help="auto: hand label, else rule check (default). label: hand-labelled responses only. rule: rule check only")
    parser.add_argument("--baseline", type=int, default=DEFAULTS["baseline"], help="Grades in the baseline, at most half of them (default 20)")
    parser.add_argument("--lam", type=float, default=DEFAULTS["lam"], help="EWMA weight of the newest grade (default 0.2)")
    parser.add_argument("--L", type=float, default=DEFAULTS["L"], help="EWMA limit width in sigma (default 3)")
    parser.add_argument("--k", type=float, default=DEFAULTS["k"], help="CUSUM slack in sigma (default 0.5)")
    parser.add_argument("--h", type=float, default=DEFAULTS["h"], help="CUSUM alarm threshold in sigma (default 5)")
    parser.add_argument("--min-sigma", type=float, default=DEFAULTS["min_sigma"], help="Smallest baseline sigma (default 0.5)")
    parser.add_argument("--export", help="Write the observations as JSON for the pipeline app")
    args = parser.parse_args()

    params = {"baseline": args.baseline, "lam": args.lam, "L": args.L, "k": args.k, "h": args.h, "min_sigma": args.min_sigma}
    judges = {j.strip() for j in args.judges.split(",")} if args.judges else None
    series, models = observations(args.responses, args.judgments, judges)
    if not series:
        sys.exit("No judgments match the responses.")
    report(series, models, args.reference, params)
    if args.export:
        data = {"params": params, "reference": args.reference,
                "judges": {jid: {"model": models.get(jid, ""), "observations": obs} for jid, obs in series.items()}}
        Path(args.export).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nDrift data written to {args.export}.")


if __name__ == "__main__":
    main()
