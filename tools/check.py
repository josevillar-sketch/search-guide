"""Data check for index.html. Run: python3 tools/check.py
Every student needs a unique id, three searches in known databases with balanced quotation
marks, a course that matches the period, and either a question, a topic, or the no-topic flag."""
import json, re, sys
from collections import Counter
from pathlib import Path

html = (Path(__file__).resolve().parent.parent / "index.html").read_text()
data = json.loads(re.search(r"var DATA = (\[.*?\]);\n", html, re.S).group(1))
dbs = set(re.findall(r"^ (\w+):\{n:", html, re.M))
research = {int(p) for p, c in re.findall(r"(\d):\"AP (Research|Seminar)\"", html) if c == "Research"}
problems = []
for sid, n in Counter(d["id"] for d in data).items():
    if n > 1:
        problems.append(f"{sid}: id used {n} times")
for d in data:
    who = f'P{d["p"]} {d["n"]}'
    if len(d["s"]) != 3:
        problems.append(f"{who}: {len(d['s'])} searches")
    for s in d["s"]:
        if s["db"] not in dbs:
            problems.append(f"{who}: unknown database {s['db']}")
        if s["q"].count('"') % 2:
            problems.append(f"{who}: unbalanced quotes in {s['q']}")
    if d["c"] != ("R" if d["p"] in research else "S"):
        problems.append(f"{who}: course {d['c']} does not match period {d['p']}")
    if not (d["q"] or d["tp"] or d["nt"]):
        problems.append(f"{who}: no question, topic, or no-topic flag")
    if not 2 <= len(d["sw"]) <= 3:
        problems.append(f"{who}: {len(d['sw'])} word swaps")
per = Counter(d["p"] for d in data)
print(f"{len(data)} students: " + ", ".join(f"P{p} {per[p]}" for p in sorted(per)))
print(f"{sum(1 for d in data if not d['q'])} without a question on record, {sum(d['nt'] for d in data)} without a topic")
if problems:
    print("FAIL\n- " + "\n- ".join(problems))
    sys.exit(1)
print("PASS")
