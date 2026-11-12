#!/usr/bin/env python3
"""Checks every link in RESOURCES.md, BOOKS.md and classroom/*.md|*.html.

Run: python3 tools/check_links.py
Exit code 1 if a link that should work does not. Links listed under the
"Pending" and "Do not use" headings of RESOURCES.md are never requested: they
are there because they refused access or could not be opened, and a refusal is
not retried by script. Sites in REFUSES_SCRIPTS open in a browser but turn away
script clients; they are listed, not failed, and need a human look.
"""
import pathlib, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
REFUSES_SCRIPTS = ('wonder.cdc.gov',)
URL = re.compile(r'https?://[^\s<>"\')\]]+')

def links(text):
    return {u.rstrip('.,;:') for u in URL.findall(text)}

def status(url):
    try:
        out = subprocess.run(
            ['curl', '-sS', '-L', '-o', '/dev/null', '-m', '25', '-A', 'Room63-link-check/1.0',
             '-w', '%{http_code}', url], capture_output=True, text=True, timeout=40)
        return out.stdout.strip() or 'ERR'
    except Exception:
        return 'ERR'

def main():
    res = (ROOT / 'RESOURCES.md').read_text(encoding='utf-8')
    cut = res.find('## Pending')
    must = links(res[:cut] if cut > 0 else res)
    soft = links(res[cut:]) if cut > 0 else set()
    must |= links((ROOT / 'BOOKS.md').read_text(encoding='utf-8'))
    for f in list((ROOT / 'classroom').glob('*.md')) + list((ROOT / 'classroom').glob('*.html')):
        must |= {u for u in links(f.read_text(encoding='utf-8')) if 'fonts.googleapis.com' not in u}
    soft -= must
    # The student library may only link to resources verified in RESOURCES.md.
    verified = links(res[:cut] if cut > 0 else res)
    lib = ROOT / 'classroom' / 'research-library.html'
    stray = sorted(u for u in links(lib.read_text(encoding='utf-8')) - verified
                   if 'fonts.googleapis.com' not in u) if lib.exists() else []
    for u in stray:
        print(f"NOT IN RESOURCES.md  {u}  (linked from the student library)")
    manual = sorted(u for u in must if any(h in u for h in REFUSES_SCRIPTS))
    auto = sorted(must - set(manual))
    with ThreadPoolExecutor(8) as ex:
        codes = dict(zip(auto, ex.map(status, auto)))
    bad = [u for u in auto if not codes[u].startswith(('2', '3'))]
    for u in auto:
        print(f"{codes[u]:>4}  {u}")
    for u in manual:
        print(f"SKIP  {u}  (refuses scripts; check in a browser)")
    print(f"\n{len(auto)} links checked, {len(bad)} failing, "
          f"{len(manual)} need a browser, {len(soft)} pending links not requested.")
    return 1 if (bad or stray) else 0

if __name__ == '__main__':
    sys.exit(main())
