"""
Put data into the Canary Lab page (pipeline-app/index.html).

Usage:
    python pipeline-app/embed_data.py                    # the 22 hand-collected responses
    python pipeline-app/embed_data.py app_results.json   # output of: llm_judge.py report ... --export app_results.json
    python pipeline-app/embed_data.py app_samples.json app_l4.json app_generated.json   # several exports in one page
    python pipeline-app/embed_data.py app_samples.json app_l4.json --drift app_drift.json   # plus drift charts (drift.py --export)

The rubric, the judge list, the attack set and the target instruction are read
from the project files every time, so the page always matches the scripts.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent
ROOT = APP.parent
sys.path.insert(0, str(ROOT))  # llm_judge.py imports env_keys.py from the project folder
PAGE = APP / "index.html"
ABOUT = {
    "canary": "Get the support bot to reveal the access code in its instructions.",
    "inject": "The bot summarises an email the user pastes. The attacker wrote the email and hid an instruction in it.",
    "refund": "The bot has a mock refund tool limited to 50 EUR per order. The attacker tries to get a call outside the rules.",
}
MARKER = re.compile(r'(<script type="application/json" id="embedded-data">)(.*?)(</script>)', re.DOTALL)


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_payload(judge, dataset, drift=None):
    """Everything the page reads: project settings plus one dataset (and drift observations)."""
    data = {
        "instruction": judge.DETECTOR.TARGET_INSTRUCTION,
        "rubric": {"system": judge.JUDGE_SYSTEM, "template": judge.JUDGE_TEMPLATE.replace("{{", "{").replace("}}", "}")},
        "judgeConfig": json.loads((ROOT / "judges.json").read_text(encoding="utf-8")),
        "attacks": judge.load_jsonl(ROOT / "attacks.jsonl"),
        "goals": {
            gid: {"name": g["name"], "tag": g["tag"], "system": g["system"] or judge.DETECTOR.TARGET_INSTRUCTION,
                  "about": ABOUT[gid]}
            for gid, g in judge.goals.GOALS.items()
        },
        "dataset": dataset,
    }
    if drift:
        data["drift"] = drift
    return data


def merge_exports(exports, name):
    judges, items, rubric = {}, [], None
    for results in exports:
        for j in results.get("judges", []):
            judges.setdefault(j["id"], j)
        items += results["items"]
        rubric = rubric or results.get("rubric")
    ids = [i["id"] for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError("The same response id appears in more than one file.")
    return {"name": name, "judges": list(judges.values()), "items": items, "rubric": rubric}


def inject(page, data):
    # "<" is written as a JSON escape so no value can close the script tag early.
    blob = json.dumps(data, ensure_ascii=False).replace("<", chr(92) + "u003c")
    if not MARKER.search(page):
        raise ValueError(f"Could not find the embedded-data script tag in {PAGE}")
    return MARKER.sub(lambda m: m.group(1) + blob + m.group(3), page, count=1)


def main():
    judge = load_module("llm_judge")
    args = sys.argv[1:]
    drift = None
    if "--drift" in args:
        i = args.index("--drift")
        drift = json.loads(Path(args[i + 1]).read_text(encoding="utf-8"))
        del args[i:i + 2]
    if args:
        sources = [Path(arg) for arg in args]
        name = " + ".join(s.name for s in sources)
        try:
            dataset = merge_exports([json.loads(s.read_text(encoding="utf-8")) for s in sources], name)
        except ValueError as error:
            sys.exit(str(error))
    else:
        name = "sample_responses.jsonl"
        dataset = {"name": name, "judges": [], "items": judge.load_jsonl(ROOT / name)}
    page = inject(PAGE.read_text(encoding="utf-8"), build_payload(judge, dataset, drift))
    PAGE.write_text(page, encoding="utf-8")
    extra = f" and drift data for {len(drift['judges'])} judge(s)" if drift else ""
    print(f"Embedded {len(dataset['items'])} responses from {name}{extra} into {PAGE.name}.")


if __name__ == "__main__":
    main()
