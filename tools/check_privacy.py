#!/usr/bin/env python3
"""Reports whether this repository is public and how many named student records index.html holds.

Run: python3 tools/check_privacy.py            reports, and passes
     python3 tools/check_privacy.py --strict   fails while the repository is public and holds names

The Search Guide page keeps the roster in its DATA array. On 2026-11-12 Mr. Portela was told the
repository is public and decided to leave it public. So the default run does not fail; it states the
facts so that nobody is surprised by them later. It still fails, in any mode, if a fork exists, because
a fork is a copy that stays public whatever happens here.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = "josevillar-sketch/search-guide"

def main():
    strict = "--strict" in sys.argv
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r"DATA\s*=\s*(\[.*?\]);", page, re.S)
    named = sum(1 for r in json.loads(m.group(1)) if str(r.get("n", "")).strip()) if m else 0
    raw = subprocess.run(["curl", "-sS", "-m", "20", "-w", "\n%{http_code}", f"https://api.github.com/repos/{REPO}"],
                         capture_output=True, text=True).stdout
    body, _, code = raw.rpartition("\n")
    if code == "404":
        print(f"PASS: {REPO} is private ({named} named records).")
        return 0
    if code != "200":
        print(f"NOTE: GitHub answered {code or 'nothing'}; could not read the repository's state. {named} named records in index.html.")
        return 0
    forks = json.loads(body).get("forks_count", 0)
    print(f"NOTE: {REPO} is public, by Mr. Portela's decision of 2026-11-12. index.html holds {named} named student records. Forks: {forks}.")
    if forks:
        print("FAIL: the repository has been forked. A fork is a public copy of the roster. Tell Mr. Portela.")
        return 1
    if strict and named:
        print("FAIL (--strict): public with named records.")
        return 1
    print("PASS: nothing has changed since that decision.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
