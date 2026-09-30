#!/usr/bin/env python3
"""Build a Room 63 book from a spec, using The Team Project (tp/) as the shell.

Usage: python3 tools/build_book.py spec.json
spec = {"key": "ip", "title": "The Individual Project", "theme": "#1f3a2c",
        "colors": {"leather": "#1f3a2c", "onlay": "#0b120e", "labelskin": "#6d1f1b"},
        "faces": [...], "tabs": [...]}          # same shapes as FACES / TABS in tp/index.html
Writes <key>/index.html next to this tools/ folder. The shell's CSS, engine and art are kept as is.

Symbolic references (resolved here, so no page number is typed by hand):
  a face may carry "id": "rubric"; a chapter board carries "folio": 3 and "title": "..."
  [[num]]          this page's number line: <div class='num'>&middot; N &middot;</div>
  [[pno:ID]]       page number of face ID          [[idx:ID]]   face index of ID
  [[jump:ID]]      data-jump='IDX' aria-label='Go to page N'
  [[pj:ID]]        inline page link button         [[gtag:ID]]  "Page N" tag button
  If "tabs" is missing it is built from the chapter boards.
Page numbers: paper faces from index 2 count 1, 2, 3...; a chapter board takes the next paper page's number.
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def strip_netlify(s):
    s = re.sub(r'<!-- This site is hosted on Netlify\..*?-->\s*', '', s, flags=re.S)
    s = re.sub(r'\s*<script async src="/\.netlify/scripts/hud[^>]*></script>\s*', '\n', s)
    return s

def resolve(faces):
    ids = {f['id']: i for i, f in enumerate(faces) if f.get('id')}
    pno, c = {}, 0
    for i, f in enumerate(faces):
        if i >= 2 and 'paper' in f['cls'].split():
            c += 1; pno[i] = c
    nxt = None
    for i in range(len(faces) - 1, -1, -1):
        if i in pno: nxt = pno[i]
        elif 'chapter' in faces[i]['cls'].split(): pno[i] = nxt
    def ref(key):
        if key not in ids: raise SystemExit('unknown page id: %s' % key)
        return ids[key]
    out = []
    for i, f in enumerate(faces):
        h = f['html']
        h = h.replace('[[num]]', "<div class='num'>&middot; %s &middot;</div>" % pno.get(i, 'x'))
        h = re.sub(r'\[\[pno:([\w-]+)\]\]', lambda m: str(pno[ref(m.group(1))]), h)
        h = re.sub(r'\[\[idx:([\w-]+)\]\]', lambda m: str(ref(m.group(1))), h)
        h = re.sub(r'\[\[jump:([\w-]+)\]\]', lambda m: "data-jump='%d' aria-label='Go to page %d'" % (ref(m.group(1)), pno[ref(m.group(1))]), h)
        h = re.sub(r'\[\[pj:([\w-]+)\]\]', lambda m: "<button type='button' class='pj' data-jump='%d' aria-label='Go to page %d'>%d</button>" % (ref(m.group(1)), pno[ref(m.group(1))], pno[ref(m.group(1))]), h)
        h = re.sub(r'\[\[gtag:([\w-]+)\]\]', lambda m: "<button type='button' class='gtag' data-jump='%d' aria-label='Go to page %d'>Page %d</button>" % (ref(m.group(1)), pno[ref(m.group(1))], pno[ref(m.group(1))]), h)
        left = re.findall(r'\[\[[^\]]*\]\]', h)
        if left: raise SystemExit('face %d: unresolved %s' % (i, left))
        out.append({'cls': f['cls'], 'html': h, 'label': f.get('label', '')})
    tabs = [{'r': str(f['folio']), 't': f['title'], 'f': i} for i, f in enumerate(faces) if 'chapter' in f['cls'].split() and 'folio' in f]
    return out, tabs

def main(path):
    spec = json.load(open(path, encoding='utf-8'))
    faces, auto_tabs = resolve(spec['faces'])
    spec['faces'] = faces
    spec.setdefault('tabs', auto_tabs)
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
