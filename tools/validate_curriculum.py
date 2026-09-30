"""Validate the curriculum: every solution must pass its check, every starter must fail.

Usage: python tools/validate_curriculum.py [week_number ...]
"""
import importlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
CHECKER = os.path.join(ROOT, "app", "sandbox", "kidcheck.py")
CONCEPTS = {"output", "variables", "input", "strings", "fstrings", "math", "types", "conditions",
            "random", "while_loops", "for_loops", "turtle", "lists", "functions", "dicts", "classes"}


def check(source, snippet):
    p = subprocess.run([sys.executable, CHECKER], input=json.dumps({"source": source, "check": snippet}),
                       capture_output=True, text=True, timeout=15)
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return {"passed": False, "message": "checker produced no JSON: " + p.stderr[-500:], "checker_error": True}


def items_for(week):
    mod = importlib.import_module(f"app.curriculum.week{week}")
    for p in getattr(mod, "PROJECTS", []):
        for s in p["steps"] + ([p["boss"]] if p.get("boss") else []):
            yield f"{p['id']}/{s['id']}", s
    for pr in getattr(mod, "PRACTICE", []):
        yield f"practice/{pr['id']}", pr


def structural(week):
    problems = []
    mod = importlib.import_module(f"app.curriculum.week{week}")
    for p in getattr(mod, "PROJECTS", []):
        for key in ("id", "week", "order", "title", "emoji", "tagline", "story", "concepts",
                    "expected_minutes", "steps", "boss", "remix"):
            if key not in p:
                problems.append(f"{p.get('id')}: missing {key}")
        for c in p.get("concepts", []):
            if c not in CONCEPTS:
                problems.append(f"{p['id']}: unknown concept {c}")
        for s in p.get("steps", []) + [p.get("boss") or {}]:
            for key in ("id", "title", "learn", "task", "starter", "hints", "solution", "check", "concepts", "xp"):
                if key not in s:
                    problems.append(f"{p['id']}/{s.get('id')}: missing {key}")
            if len(s.get("hints", [])) != 3:
                problems.append(f"{p['id']}/{s.get('id')}: needs exactly 3 hints")
            for c in s.get("concepts", []):
                if c not in CONCEPTS:
                    problems.append(f"{p['id']}/{s.get('id')}: unknown concept {c}")
    for pr in getattr(mod, "PRACTICE", []):
        if pr.get("concept") not in CONCEPTS:
            problems.append(f"practice/{pr.get('id')}: unknown concept {pr.get('concept')}")
    return problems


def main():
    weeks = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]
    problems = []
    jobs = []
    for w in weeks:
        try:
            problems += structural(w)
            jobs += list(items_for(w))
        except ModuleNotFoundError:
            print(f"week{w}: not written yet")
    def one(job):
        name, s = job
        out = []
        sol = check(s["solution"], s["check"])
        if not sol["passed"]:
            out.append(f"{name}: SOLUTION FAILS -> {sol['message']}")
        st = check(s["starter"], s["check"])
        if st["passed"]:
            out.append(f"{name}: starter already passes (should fail)")
        if st.get("checker_error"):
            out.append(f"{name}: checker error on starter -> {st['message']}")
        return out
    with ThreadPoolExecutor(8) as ex:
        for res in ex.map(one, jobs):
            problems += res
    print(f"checked {len(jobs)} steps/practice items")
    for p in problems:
        print(" -", p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
