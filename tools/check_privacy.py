#!/usr/bin/env python3
"""Fails while this repository is public and index.html holds student names.

Run: python3 tools/check_privacy.py
The Search Guide page keeps the roster in its DATA array. That is fine in a private repository and a
privacy breach in a public one. This check asks GitHub, without credentials, whether the repository can
be seen by anyone. Exit code 1 means: make the repository private (GitHub, Settings, General, Danger
Zone, Change repository visibility) before doing anything else.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = "josevillar-sketch/search-guide"

def main():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r"DATA\s*=\s*(\[.*?\]);", page, re.S)
    named = sum(1 for r in json.loads(m.group(1)) if str(r.get("n", "")).strip()) if m else 0
    out = subprocess.run(["curl", "-sS", "-m", "20", "-o", "/dev/null", "-w", "%{http_code}",
                          f"https://api.github.com/repos/{REPO}"], capture_output=True, text=True).stdout.strip()
    if out == "200" and named:
        print(f"FAIL: {REPO} is PUBLIC and index.html holds {named} named student records.")
        print("Make the repository private now: GitHub, Settings, General, Danger Zone, Change repository visibility.")
        return 1
    if out == "404":
        print(f"PASS: {REPO} is not visible without signing in ({named} named records stay private).")
        return 0
    if not named:
        print("PASS: index.html holds no named student records.")
        return 0
    print(f"UNKNOWN: GitHub answered {out or 'nothing'}; could not tell whether the repository is public. Check by hand.")
    return 2

if __name__ == "__main__":
    sys.exit(main())
