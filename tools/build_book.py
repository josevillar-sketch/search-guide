#!/usr/bin/env python3
"""Build a Room 63 book from a spec, using The Team Project (tp/) as the shell.

Usage: python3 tools/build_book.py spec.json
spec = {"key": "ip", "title": "The Individual Project", "theme": "#1f3a2c",
        "colors": {"leather": "#1f3a2c", "onlay": "#0b120e", "labelskin": "#6d1f1b"},
        "faces": [...], "tabs": [...]}          # same shapes as FACES / TABS in tp/index.html
Writes <key>/index.html next to this tools/ folder. The shell's CSS, engine and art are kept as is.
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def strip_netlify(s):
    s = re.sub(r'<!-- This site is hosted on Netlify\..*?-->\s*', '', s, flags=re.S)
    s = re.sub(r'\s*<script async src="/\.netlify/scripts/hud[^>]*></script>\s*', '\n', s)
    return s

def main(path):
    spec = json.load(open(path, encoding='utf-8'))
    shell = strip_netlify(open(os.path.join(ROOT, 'tp', 'index.html'), encoding='utf-8').read())
    faces, tabs = spec['faces'], spec['tabs']
    assert len(faces) % 2 == 0, 'FACES must have an even count (front and back of each leaf)'
    data = 'var FACES=' + json.dumps(faces, ensure_ascii=False) + ';var TABS=' + json.dumps(tabs, ensure_ascii=False) + ';'
    data = data.replace('</', '<\\/')
    n = 0
    def swap(m):
        nonlocal n; n += 1
        return m.group(1) + data + '</script>'
    shell = re.sub(r'(<script>)var FACES=.*?</script>', swap, shell, count=1, flags=re.S)
    assert n == 1, 'FACES script not found in shell'
    shell = shell.replace('<title>The Team Project</title>', '<title>%s</title>' % spec['title'])
    shell = re.sub(r'<meta name="theme-color" content="[^"]+">', '<meta name="theme-color" content="%s">' % spec['theme'], shell, count=1)
    c = spec.get('colors', {})
    if c.get('leather'):
        shell = shell.replace('.face.lthr,html .face.board.lthr{background:#2e2145!important}', '.face.lthr,html .face.board.lthr{background:%s!important}' % c['leather'])
        shell = shell.replace('.A-leather{fill:#2e2145}', '.A-leather{fill:%s}' % c['leather'])
    if c.get('onlay'):
        shell = shell.replace('.A-onlay{fill:#0d0a10}', '.A-onlay{fill:%s}' % c['onlay'])
    if c.get('labelskin'):
        shell = shell.replace('.A-labelskin{fill:#1e4a2e}', '.A-labelskin{fill:%s}' % c['labelskin'])
    # keep the shell's styling hooks (book-tp) and add the book's own key for anything specific
    shell = shell.replace("classList.add('book-tp','pb-B')", "classList.add('book-tp','book-%s','pb-B')" % spec['key'])
    shell = shell.replace('class="book-tp pb-B"', 'class="book-tp book-%s pb-B"' % spec['key'])
    out = os.path.join(ROOT, spec['key'], 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(shell)
    print('wrote', out, len(shell), 'bytes,', len(faces), 'faces,', len(tabs), 'folios')

if __name__ == '__main__':
    main(sys.argv[1])
