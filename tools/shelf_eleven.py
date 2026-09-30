#!/usr/bin/env python3
"""Put Books S2 (ip) and S3 (ex) on the Room 63 Library shelf.

Reads the nine-book landing page from git (the baseline commit), writes index.html.
Usage: python3 tools/shelf_eleven.py <baseline-commit> <objects.json> <copy.json>

What it does, in both rooms (the wide desktop room and the tall phone room):
  1. Draws two new vellum spines (sp-ip, sp-ex) from The Team Project's spine.
  2. Makes every spine thinner without touching its lettering: the leather is
     squeezed, and the titles, volume marks, fleurons and headband beads are
     counter-scaled so they keep their drawn size.
  3. Re-spaces the eleven books over the same length of shelf and redraws the
     three brass plates to fit their groups.
  4. Moves each object resting on the book tops with the book beneath it.
  5. Adds the two books to the syllabus, bibliography, cards and descriptions.
"""
import json, re, subprocess, sys

BASE, OBJS, COPY = sys.argv[1], sys.argv[2], sys.argv[3]
ROOT = __file__.rsplit('/tools/', 1)[0]
s = subprocess.run(['git', '-C', ROOT, 'show', BASE + ':index.html'], capture_output=True, text=True, check=True).stdout
objs = json.load(open(OBJS))
copy = json.load(open(COPY))

F_ER, F_S = 0.85, 0.65          # width factors: Every Course and Research books, Seminar books
ORDER = ['log', 'manual', 'ai', 'fg', 'pd', 'pp', 'paper', 'pr', 'tp', 'ip', 'ex']
GROUP = {k: ('E' if i < 5 else 'R' if i < 8 else 'S') for i, k in enumerate(ORDER)}
FACT = {k: (F_S if GROUP[k] == 'S' else F_ER) for k in ORDER}

def once(pat, rep, text, flags=0):
    new, n = re.subn(pat, rep, text, count=1, flags=flags)
    assert n == 1, 'pattern not found: ' + pat[:80]
    return new

# ---------- 1. new spine symbols and their paint ----------
NEW = {
    'ip': {'label': '#173a28', 'tool': '#23533d', 'bead': '#1e4a2e', 'num': 'S2',
           'lines': [('THE INDIVIDUAL', 13.5), ('PROJECT', 13.5)]},
    'ex': {'label': '#16213f', 'tool': '#26365e', 'bead': '#1b2a4a', 'num': 'S3',
           'lines': [('THE END-OF-COURSE', 12.2), ('EXAM', 15.0)]},
}

def grab(pattern):
    m = re.search(pattern, s, flags=re.S)
    assert m, pattern
    return m.group(0)

tp_defs = [grab(r'<linearGradient id="g-sp-tp".*?</linearGradient>'),
           grab(r'<pattern id="hb-tp".*?</pattern>'),
           grab(r'<clipPath id="c-tp">.*?</clipPath>'),
           grab(r'<linearGradient id="g-tp-0".*?</linearGradient>')]
tp_sym = grab(r'<symbol id="sp-tp".*?</symbol>')

def title_texts(key, lines, c=26.0, y=114.9, gap=2.0):
    """Stack of rotated title lines centred on the spine at x = c (cap height about 0.7 em)."""
    caps = [0.7 * size for _, size in lines]
    total = sum(caps) + gap * (len(lines) - 1)
    x = c + total / 2
    out = []
    for i, ((text, size), cap) in enumerate(zip(lines, caps)):
        x -= cap                                   # baseline of this line
        tr = 'translate(%.1f %.1f) scale(1.0000 1) rotate(90)' % (x, y)
        out.append('<text class="tv dk" transform="translate(-.5 -.5) %s" style="font-size:%.2fpx">%s</text>' % (tr, size, text))
        out.append('<text class="tv" fill="url(#g-%s-%d)" transform="%s" style="font-size:%.2fpx">%s</text>' % (key, i, tr, size, text))
        x -= gap
    return ''.join(out)

new_defs, new_syms = [], []
for key, d in NEW.items():
    defs = [t.replace('-tp', '-' + key) for t in tp_defs]
    defs[1] = defs[1].replace('#6d1f1b', d['bead'])
    defs.append(defs[3].replace('id="g-%s-0"' % key, 'id="g-%s-1"' % key))
    new_defs += defs
    sym = tp_sym.replace('sp-tp', 'sp-' + key).replace('hb-tp', 'hb-' + key).replace('c-tp', 'c-' + key)
    sym = sym.replace('#5e1a14', d['label']).replace('#7a2a1e', d['tool'])
    sym = sym.replace('>S1</text>', '>%s</text>' % d['num'])
    sym = re.sub(r'<text class="tv dk".*?</text><text class="tv".*?</text>', title_texts(key, d['lines']), sym, count=1, flags=re.S)
    new_syms.append(sym)
s = once(r'(<linearGradient id="g-tp-0".*?</linearGradient>)', lambda m: m.group(1) + ''.join(new_defs), s, re.S)
s = once(r'(<symbol id="sp-tp".*?</symbol>)', lambda m: m.group(1) + ''.join(new_syms), s, re.S)

# ---------- 2. thinner spines, lettering kept at its drawn size ----------
def narrow(sym, f):
    c = float(re.search(r'<text class="imp" x="([\d.]+)"', sym).group(1))
    unsq = 'translate(%.2f 0) scale(%.4f 1) translate(-%.2f 0)' % (c, 1 / f, c)
    def tv(m):
        pre, x, y, sx = m.group(1), float(m.group(2)), m.group(3), float(m.group(4))
        x2 = c - (c - x) / f
        return '%stranslate(%.2f %s) scale(%.4f 1) rotate(90)' % (pre, x2, y, sx / f)
    sym = re.sub(r'((?:translate\(-\.5 -\.5\) )?)translate\(([\d.]+) ([\d.]+)\) scale\(([\d.]+) 1\) rotate\(90\)', tv, sym)
    sym = re.sub(r'<text class="imp" ', '<text class="imp" transform="%s" ' % unsq, sym)
    # fleurons: filled, unstroked tooling paths drawn as small rosettes (they contain arc dots)
    def fl(m):
        tag = m.group(0)
        if 'stroke=' in tag or 'a.' not in tag: return tag
        return tag.replace('<path ', '<path transform="%s" ' % unsq, 1)
    sym = re.sub(r'<path d="[^"]*"[^>]*/>', fl, sym)
    return sym

for k in ORDER:
    s = once(r'<symbol id="sp-%s".*?</symbol>' % k, lambda m: narrow(m.group(0), FACT[k]), s, re.S)
    s = once(r'(<pattern id="hb-%s" )' % k, lambda m: m.group(1) + 'patternTransform="scale(%.4f 1)" ' % (1 / FACT[k]), s)

# ---------- 3. positions ----------
# tall room: 390 units wide, first rule block; wide room: 1600 units wide, rule block inside the desktop media query
LAYOUT = {
    'tall': {'x0': 23.1, 'x1': 366.9, 'ggap': 4.5, 'w': {'log': 35.2, 'manual': 34.4, 'ai': 33.6, 'fg': 34.4, 'pd': 34.4, 'pp': 35.2, 'paper': 35.2, 'pr': 37.6, 'tp': 44.8},
             'units': 390, 'plate_h': 13.4, 'plate_y': 1073},
    'wide': {'x0': 45.0, 'x1': 475.0, 'ggap': 5.6, 'w': {'log': 44, 'manual': 43, 'ai': 42, 'fg': 43, 'pd': 43, 'pp': 44, 'paper': 44, 'pr': 47, 'tp': 56},
             'units': 1600, 'plate_h': 18.5, 'plate_y': 802},
}

def book_rule(block, key):
    m = re.search(r'\.book\[data-key=%s\]\{left:calc\(var\(--a\)\*([\d.]+)\);top:calc\(var\(--a\)\*([\d.]+)\);width:calc\(var\(--a\)\*([\d.]+)\);height:calc\(var\(--a\)\*([\d.]+)\)\}' % key, block)
    return m

m_all = list(re.finditer(r'\.book\[data-key=log\]\{left', s))
assert len(m_all) == 2
starts = [m.start() for m in m_all]
blocks = {'tall': (starts[0], s.index('.plate-S{', starts[0])), 'wide': (starts[1], s.index('.plate-S{', starts[1]))}

plan = {}
for name, L in LAYOUT.items():
    a, b = blocks[name]
    block = s[a:s.index('}', b) + 1]
    old = {}
    for k in ORDER[:9]:
        m = book_rule(block, k)
        old[k] = tuple(float(v) for v in m.groups())
    old['ip'] = old['ex'] = old['tp']
    widths = {k: L['w'][k if k in L['w'] else 'tp'] * FACT[k] for k in ORDER}
    inner = (L['x1'] - L['x0'] - sum(widths.values()) - 2 * L['ggap']) / 8
    x, pos = L['x0'], {}
    for i, k in enumerate(ORDER):
        if i: x += L['ggap'] if GROUP[k] != GROUP[ORDER[i - 1]] else inner
        pos[k] = (x, old[k][1], widths[k], old[k][3]); x += widths[k]
    plan[name] = {'old': old, 'new': pos, 'inner': inner}
    rules = ''.join('.book[data-key=%s]{left:calc(var(--a)*%.2f);top:calc(var(--a)*%.1f);width:calc(var(--a)*%.2f);height:calc(var(--a)*%.1f)}' % ((k,) + pos[k]) for k in ORDER)
    # plates: E spans log..pd, R spans pp..pr, S spans tp..ex, with the old insets
    pe = (pos['log'][0] + 2.4, pos['pd'][0] + pos['pd'][2] - 2.4)
    pr_ = (pos['pp'][0] + 2.4, pos['pr'][0] + pos['pr'][2] - 2.4)
    ps = (pos['tp'][0] - 3.2, pos['ex'][0] + pos['ex'][2] + 3.1)
    plates = {'E': pe, 'R': pr_, 'S': ps}
    plan[name]['plates'] = plates
    prules = ''.join('.plate-%s{left:calc(var(--a)*%.2f);top:calc(var(--a)*%s);width:calc(var(--a)*%.2f);height:calc(var(--a)*%s)}' % (g, lo, L['plate_y'], hi - lo, L['plate_h']) for g, (lo, hi) in plates.items())
    old_block = s[a:s.index('}', b) + 1]
    s = s[:a] + rules + prules + s[a + len(old_block):]
    # recompute the second block's offsets after the first edit
    m_all = list(re.finditer(r'\.book\[data-key=log\]\{left', s)); starts = [m.start() for m in m_all]
    blocks = {'tall': (starts[0], s.index('.plate-S{', starts[0])), 'wide': (starts[1], s.index('.plate-S{', starts[1]))}

# plate drawings: same lettering, new length
def plate_svg(svg, new_w):
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    w, h = float(vb.group(1)), float(vb.group(2))
    nw = round(w * new_w, 2)
    def num(x): return ('%.2f' % x).rstrip('0').rstrip('.')
    svg = svg.replace('viewBox="0 0 %s %s"' % (vb.group(1), vb.group(2)), 'viewBox="0 0 %s %s"' % (num(nw), vb.group(2)))
    svg = re.sub(r'(<rect x="0" y="[\d.]+" width=")%s"' % re.escape(vb.group(1)), lambda m: m.group(1) + num(nw) + '"', svg)
    svg = svg.replace('H%s"' % num(w - .8), 'H%s"' % num(nw - .8)).replace('H%s' % num(w - .8), 'H%s' % num(nw - .8))
    svg = re.sub(r'<text x="[\d.]+"', '<text x="%s"' % num(nw / 2), svg)
    for dx in (3.1 - w, ):
        pass
    svg = svg.replace('cx="%s"' % num(w - 3.1), 'cx="%s"' % num(nw - 3.1))
    svg = svg.replace('M%s ' % num(w - 4.1), 'M%s ' % num(nw - 4.1)).replace('L%s ' % num(w - 2.2), 'L%s ' % num(nw - 2.2))
    return svg

OLD_PLATE = {'tall': {'E': 173.2, 'R': 106.2, 'S': 51.1}, 'wide': {'E': 217, 'R': 133, 'S': 64.9}}
for g in 'ERS':
    for lay, cls in (('wide', 'pl-d'), ('tall', 'pl-p')):
        lo, hi = plan[lay]['plates'][g]
        ratio = (hi - lo) / OLD_PLATE[lay][g]
        s = once(r'(<i class="plate plate-%s %s" aria-hidden="true">)(<svg.*?</svg>)' % (g, cls), lambda m: m.group(1) + plate_svg(m.group(2), ratio), s, re.S)

# ---------- 4. objects on the book tops move with their book ----------
for lay, cls in (('wide', 'ovs-d'), ('tall', 'ovs-p')):
    info, P = objs[lay], plan[lay]
    a = s.index('class="ovs %s"' % cls)
    for o in info['objs']:
        cx = (o['l'] + o['r']) / 2
        def dist(k):
            l, _, w, _ = P['old'][k]
            return 0 if l <= cx <= l + w else min(abs(cx - l), abs(cx - l - w))
        k = min(ORDER[:9], key=dist)
        ol, _, ow, _ = P['old'][k]; nl, _, nw, _ = P['new'][k]
        shift = (nl + nw / 2) - (ol + ow / 2)
        left = float(re.search(r'left:([\d.]+)%', o['style']).group(1))
        new_style = o['style'].replace('left:%s%%' % re.search(r'left:([\d.]+)%', o['style']).group(1), 'left:%.3f%%' % (left + shift / LAYOUT[lay]['units'] * 100))
        tag = 'data-o="%s"' % o['o']
        i = s.index(tag, a)
        while True:              # the same object can appear more than once in a room; match its style
            j = s.find('style="' + o['style'] + '"', i)
            if 0 <= j - i < 200: break
            i = s.index(tag, i + 1)
        s = s[:j] + 'style="' + new_style + '"' + s[j + len(o['style']) + 8:]
        print('%-5s %-15s on %-6s moved %+.1f units' % (lay, o['o'], k, shift))

# ---------- 5. the words ----------
COURSE = 'For AP Seminar, periods 2, 5, 6, 7 and 8.'
anchors = ''
for key, vol, title, med in (('ip', 'Book S2', copy['ip']['title'], 'Vellum, green label, gilt tooling.'), ('ex', 'Book S3', copy['ex']['title'], 'Vellum, navy label, gilt tooling.')):
    anchors += ('<a class="book" data-key="%s" href="%s/" data-vol="%s" data-course="%s" data-group="S" data-title="%s" data-med="%s" aria-describedby="d-%s">'
                '<span class="sr">%s, %s. %s</span><svg class="art" viewBox="-2 -9 56 310" aria-hidden="true" focusable="false"><use href="#sp-%s" x="-2" y="-9"/></svg>'
                '<i class="rib" aria-hidden="true"></i></a>') % (key, key, vol, COURSE, title, med, key, title, vol, COURSE, key)
s = once(r'(<use href="#sp-tp" x="-2" y="-9"/></svg><i class="rib" aria-hidden="true"></i></a>)', lambda m: m.group(1) + anchors, s)
s = s.replace('<svg class="art" viewBox=', '<svg class="art" preserveAspectRatio="none" viewBox=')

for key in ('ip', 'ex'):
    s = s.replace('main[data-start=tp] .book[data-key=tp] .rib', 'main[data-start=tp] .book[data-key=tp] .rib,main[data-start=%s] .book[data-key=%s] .rib' % (key, key), 1) if key == 'ip' else \
        s.replace('main[data-start=ip] .book[data-key=ip] .rib', 'main[data-start=ip] .book[data-key=ip] .rib,main[data-start=ex] .book[data-key=ex] .rib', 1)
    s = s.replace('main[data-start=tp] .card[data-key=tp] .ps', 'main[data-start=tp] .card[data-key=tp] .ps,main[data-start=%s] .card[data-key=%s] .ps' % (key, key), 1) if key == 'ip' else \
        s.replace('main[data-start=ip] .card[data-key=ip] .ps', 'main[data-start=ip] .card[data-key=ip] .ps,main[data-start=ex] .card[data-key=ex] .ps', 1)

s = once(r'(<span id="d-tp">.*?</span>)', lambda m: m.group(1) + '<span id="d-ip">%s</span><span id="d-ex">%s</span>' % (copy['ip']['hover'], copy['ex']['hover']), s, re.S)
card = '<article class="card" data-key="%s"><p class="pv">%s</p><h3 class="pt">%s</h3><span class="orn" aria-hidden="true"></span><p class="pd">%s</p><p class="ps">Start here.</p><a class="go" href="%s/">Begin reading</a><p class="pi">Room 63 Library, 2026-27</p></article>'
s = once(r'(<article class="card" data-key="tp">.*?</article>)', lambda m: m.group(1) + card % ('ip', 'Book S2', copy['ip']['title'], copy['ip']['card'], 'ip') + card % ('ex', 'Book S3', copy['ex']['title'], copy['ex']['card'], 'ex'), s, re.S)

s = once(r'(<li><b>S1\. The Team Project\.</b>.*?</li>)', lambda m: m.group(1) + '<li><b>S2. %s.</b> <i>AP Seminar.</i> %s</li><li><b>S3. %s.</b> <i>AP Seminar.</i> %s</li>' % (copy['ip']['title'], copy['ip']['syllabus'], copy['ex']['title'], copy['ex']['syllabus']), s, re.S)
s = once(r'(<li>Room 63 Library\. <i>The Team Project</i>\. Book S1, 2026&#8209;27\.</li>)', lambda m: m.group(1) + '<li>Room 63 Library. <i>%s</i>. Book S2, 2026&#8209;27.</li><li>Room 63 Library. <i>%s</i>. Book S3, 2026&#8209;27.</li>' % (copy['ip']['title'], copy['ex']['title']), s)

for old, new in copy['replace']:
    assert old in s, 'missing text: ' + old
    s = s.replace(old, new)

open(ROOT + '/index.html', 'w', encoding='utf-8').write(s)
print('inner gaps', {k: round(v['inner'], 2) for k, v in plan.items()})
json.dump({k: {'new': v['new'], 'plates': v['plates']} for k, v in plan.items()}, open('/dev/stdout', 'w'), indent=None)
print()
