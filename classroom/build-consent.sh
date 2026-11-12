#!/bin/sh
set -eu
# Rebuilds consent-templates.docx from consent-templates.md. Run from this folder.
# The forms are Word files that families and students edit, so they use the two faces every computer has and that
# DESIGN.md names as the fallbacks: Georgia for titles, Verdana for text. Same ink, same title rule as the handouts.
# A supported soffice/libreoffice renderer is required. Both the stress copy and
# the actual distribution render must keep every form on its own page.
for required in pandoc python3 pdfinfo; do
  if ! command -v "$required" >/dev/null 2>&1; then
    echo "BLOCKED consent: missing build dependency $required"; exit 1
  fi
done
renderer=$(command -v soffice || command -v libreoffice || true)
if [ -z "$renderer" ]; then
  echo "BLOCKED consent: renderer unavailable; page check did not run"; exit 1
fi
pandoc -f markdown+hard_line_breaks consent-templates.md -o consent-templates.docx
python3 - <<'PY'
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor

INK, BRASS = RGBColor(0x1d, 0x18, 0x12), RGBColor(0x6d, 0x4f, 0x14)
d = Document('consent-templates.docx')
for s in d.sections:
    s.top_margin = s.bottom_margin = Inches(0.7); s.left_margin = s.right_margin = Inches(1.0)

def face(st, name):
    st.font.name = name
    rpr = st.element.get_or_add_rPr()
    fonts = rpr.find(qn('w:rFonts'))
    for a in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):   # a theme face would override the named one
        if fonts.get(qn('w:' + a)) is not None: del fonts.attrib[qn('w:' + a)]
    for a in ('ascii', 'hAnsi', 'cs'): fonts.set(qn('w:' + a), name)

def rule_below(st, size_eighths=18, space=6):
    ppr = st.element.get_or_add_pPr()
    for old in ppr.findall(qn('w:pBdr')): ppr.remove(old)
    bdr = OxmlElement('w:pBdr'); b = OxmlElement('w:bottom')
    for k, v in (('val', 'single'), ('sz', str(size_eighths)), ('space', str(space)), ('color', '1D1812')): b.set(qn('w:' + k), v)
    bdr.append(b); ppr.append(bdr)

for st in d.styles:
    if st.type != 1: continue
    face(st, 'Verdana'); st.font.color.rgb = INK
    pf = st.paragraph_format
    if st.name in ('Normal', 'Body Text', 'First Paragraph', 'Compact'):
        st.font.size = Pt(10); pf.space_after = Pt(4); pf.space_before = Pt(0); pf.line_spacing = 1.12
    if st.name == 'Heading 1':
        face(st, 'Georgia'); st.font.size = Pt(19); st.font.bold = True
        pf.space_before = Pt(0); pf.space_after = Pt(8); pf.keep_with_next = True; rule_below(st)
    if st.name == 'Title':
        face(st, 'Georgia'); st.font.size = Pt(28); st.font.bold = True
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT; pf.space_after = Pt(8); rule_below(st)
    if st.name == 'Subtitle':
        st.font.size = Pt(10); st.font.bold = True; st.font.color.rgb = BRASS
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT; pf.space_after = Pt(16)
# The Spanish guardian form has more prose. Keep its 10pt text, line spacing,
# choice boxes and signature heights; reduce only redundant paragraph-after air.
spanish_guardian = False
for par in d.paragraphs:
    if par.style.name == 'Heading 1':
        spanish_guardian = par.text.startswith('Formulario de permiso para padres o tutores')
    elif spanish_guardian and par.style.name in ('Normal', 'Body Text', 'First Paragraph', 'Compact'):
        par.paragraph_format.space_after = Pt(2)
# ---- Choices and signatures are places a parent writes, so they are drawn, not typed.
# A choice is a ruled box on its own line (a typed box character changes size from one computer to the next,
# and two opposite choices on one line invite a tick between them). A name, signature or date is a full-width rule.
import re
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_CELL_VERTICAL_ALIGNMENT
BOX = '☐'

def cell_borders(cell, on):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:tcBorders')): tcPr.remove(old)
    b = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        e = OxmlElement('w:' + side)
        if on:
            for k, v in (('val', 'single'), ('sz', '12'), ('space', '0'), ('color', '1D1812')): e.set(qn('w:' + k), v)
        else: e.set(qn('w:val'), 'nil')
        b.append(e)
    tcPr.append(b)

def lines_of(par):
    """The paragraph as lines of (text, bold) pieces, split at line breaks."""
    lines, cur = [], []
    for r in par.runs:
        bold = bool(r.bold)
        for node in r._r:
            if node.tag == qn('w:t'): cur.append((node.text or '', bold))
            elif node.tag == qn('w:br'): lines.append(cur); cur = []
    lines.append(cur)
    return lines

def choices_of(line):
    """Split one line at each box: the words before the first box, then one list of pieces per choice."""
    lead, items, cur = [], [], None
    for text, bold in line:
        parts = text.split(BOX)
        for i, part in enumerate(parts):
            if i > 0: cur = []; items.append(cur)
            if part: (lead if cur is None else cur).append((part, bold))
    strip = lambda ps: [(t, b) for t, b in ps if t.strip()] and ps
    return strip(lead), [strip(i) for i in items]

def write(par, pieces):
    pieces = list(pieces)
    if pieces: pieces[0] = (pieces[0][0].lstrip(), pieces[0][1]); pieces[-1] = (pieces[-1][0].rstrip(), pieces[-1][1])
    for text, bold in pieces:
        if text: par.add_run(text).bold = bold or None
    par.paragraph_format.space_after = Pt(0); par.paragraph_format.space_before = Pt(0)

def bottom_rule(cell):
    cell_borders(cell, False)
    e = cell._tc.get_or_add_tcPr().find(qn('w:tcBorders')).find(qn('w:bottom'))
    for k, v in (('val', 'single'), ('sz', '8'), ('space', '0'), ('color', '1D1812')): e.set(qn('w:' + k), v)

for par in list(d.paragraphs):
    text = par.text
    if BOX in text:
        rows = []                                    # ('lead', pieces) or ('box', pieces)
        for line in lines_of(par):
            lead, items = choices_of(line)
            if lead: rows.append(('lead', lead))
            rows += [('box', i) for i in items]
        table = d.add_table(rows=2 * len(rows), cols=2); table.autofit = False
        table.columns[0].width = Inches(0.22); table.columns[1].width = Inches(6.12)
        grid = table._tbl.tblGrid.findall(qn('w:gridCol'))
        grid[0].set(qn('w:w'), str(int(0.22 * 1440))); grid[1].set(qn('w:w'), str(int(6.12 * 1440)))
        for i, (kind, pieces) in enumerate(rows):
            row, gap = table.rows[2 * i], table.rows[2 * i + 1]
            row.height = Inches(0.21); row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            gap.height = Inches(0.045); gap.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            for r in (row, gap):
                r.cells[0].width = Inches(0.22); r.cells[1].width = Inches(6.12)
                for c in r.cells:
                    cell_borders(c, False); c.paragraphs[0].paragraph_format.space_after = Pt(0)
            for c in gap.cells: c.paragraphs[0].paragraph_format.line_spacing = Pt(4)
            if kind == 'box': cell_borders(row.cells[0], True); target = row.cells[1]
            else: target = row.cells[0].merge(row.cells[1])
            target.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            write(target.paragraphs[0], pieces)
            if kind == 'box': target.paragraphs[0].paragraph_format.left_indent = Inches(0.08)
        par._p.addprevious(table._tbl); par._p.getparent().remove(par._p)
    elif re.search(r'_{5,}', text):
        labels = [m.strip() for m in re.findall(r'([^_:]+):\s*_{5,}', text)]
        table = d.add_table(rows=len(labels), cols=1); table.autofit = False       # one full-width rule per label
        table.columns[0].width = Inches(6.34); table._tbl.tblGrid.findall(qn('w:gridCol'))[0].set(qn('w:w'), str(int(6.34 * 1440)))
        for row, label in zip(table.rows, labels):
            row.height = Inches(0.35); row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            cell = row.cells[0]; cell.width = Inches(6.34); bottom_rule(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.BOTTOM
            write(cell.paragraphs[0], [(label + ':', False)])
        par._p.addprevious(table._tbl); par._p.getparent().remove(par._p)

# ---- Keep each form's ending together. A student replaces the brackets with their own words; if that adds a line,
# the choices and the signature rows must move to the next page as one block, never a date row on its own.
from docx.table import Table
body = d.element.body
tables = [el for el in body if el.tag == qn('w:tbl')]
for tbl in tables:
    t = Table(tbl, d)
    pr = tbl.tblPr; mar = OxmlElement('w:tblCellMar')            # no cell inset, so labels line up with the text above
    for side in ('left', 'right'):
        e = OxmlElement('w:' + side); e.set(qn('w:w'), '0'); e.set(qn('w:type'), 'dxa'); mar.append(e)
    pr.append(mar)
    nxt = tbl.getnext()
    last_of_block = nxt is None or nxt.tag != qn('w:tbl')
    for i, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr(); trPr.append(OxmlElement('w:cantSplit'))
        if last_of_block and i == len(t.rows) - 1: continue
        for c in row.cells:
            for par in c.paragraphs: par.paragraph_format.keep_with_next = True
    prev = tbl.getprevious()                                       # the line before the choices stays with them
    if prev is not None and prev.tag == qn('w:p'):
        ppr = prev.get_or_add_pPr()
        if ppr.find(qn('w:keepNext')) is None: ppr.append(OxmlElement('w:keepNext'))

d.save('consent-templates.docx')
PY
# Page check. Verdana and Georgia may not be installed where this runs, and LibreOffice would then swap in a narrower
# face and undercount. The DejaVu copy stresses horizontal fit; vertical substitution metrics can still differ,
# so the actual distribution DOCX is also rendered and checked separately below.
if [ -n "${CONSENT_OUT:-}" ]; then
  mkdir -p "$CONSENT_OUT"; chmod 700 "$CONSENT_OUT"
  tmp=$(mktemp -d "$CONSENT_OUT/consent-XXXXXX")
else
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' 0
fi
python3 - "$tmp" <<'PY'
import sys, zipfile
src, dst = zipfile.ZipFile('consent-templates.docx'), zipfile.ZipFile(sys.argv[1] + '/check.docx', 'w', zipfile.ZIP_DEFLATED)
for item in src.infolist():
    data = src.read(item.filename)
    if item.filename.endswith('.xml'):
        data = data.replace(b'"Verdana"', b'"DejaVu Sans"').replace(b'"Georgia"', b'"DejaVu Serif"')
    dst.writestr(item, data)
dst.close()
PY
  "$renderer" --headless --convert-to pdf --outdir "$tmp" "$tmp/check.docx" >"$tmp/render.log" 2>&1
  if [ ! -s "$tmp/check.pdf" ]; then
    echo "FAIL consent: renderer did not produce a fresh PDF"; exit 1
  fi
  pages=$(pdfinfo "$tmp/check.pdf" 2>/dev/null | awk '/^Pages/{print $2}')
  if [ "$pages" = "9" ]; then echo "ok   consent-templates.docx  9 pages: cover, six forms, two survey screens"
  else echo "FAIL consent-templates.docx  $pages pages, expected 9: a form has run onto a second page"; exit 1; fi
  # Also retain the actual distribution DOCX as rendered by this runtime. Its fonts may be substituted;
  # this is distinct from the deliberately wider DejaVu check and from Microsoft Word on a family computer.
  mkdir "$tmp/distribution"
  "$renderer" --headless --convert-to pdf --outdir "$tmp/distribution" consent-templates.docx >"$tmp/distribution/render.log" 2>&1
  actual="$tmp/distribution/consent-templates.pdf"
  if [ ! -s "$actual" ]; then echo "FAIL consent: actual distribution render is missing"; exit 1; fi
  actual_pages=$(pdfinfo "$actual" | awk '/^Pages/{print $2}')
  if [ "$actual_pages" != "9" ]; then echo "FAIL consent: distribution render has $actual_pages pages, expected 9"; exit 1; fi
  echo "ok   consent distribution render  9 pages: runtime conversion; fonts may be substituted"
  if command -v pdffonts >/dev/null 2>&1; then pdffonts "$actual" >"$tmp/distribution/fonts.txt"; fi
