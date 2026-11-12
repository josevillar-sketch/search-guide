#!/bin/sh
# Rebuilds consent-templates.docx from consent-templates.md. Run from this folder.
# The forms are Word files that families and students edit, so they use the two faces every computer has and that
# DESIGN.md names as the fallbacks: Georgia for titles, Verdana for text. Same ink, same title rule as the handouts.
# If LibreOffice is installed, the script also checks that every form still fits on its own page.
pandoc -f markdown+hard_line_breaks consent-templates.md -o consent-templates.docx && python3 - <<'PY'
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
        face(st, 'Georgia'); st.font.size = Pt(20); st.font.bold = True
        pf.space_before = Pt(0); pf.space_after = Pt(8); pf.keep_with_next = True; rule_below(st)
    if st.name == 'Title':
        face(st, 'Georgia'); st.font.size = Pt(28); st.font.bold = True
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT; pf.space_after = Pt(8); rule_below(st)
    if st.name == 'Subtitle':
        st.font.size = Pt(10); st.font.bold = True; st.font.color.rgb = BRASS
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT; pf.space_after = Pt(16)
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
            row.height = Inches(0.22); row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
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
            row.height = Inches(0.37); row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            cell = row.cells[0]; cell.width = Inches(6.34); bottom_rule(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.BOTTOM
            write(cell.paragraphs[0], [(label + ':', False)])
        par._p.addprevious(table._tbl); par._p.getparent().remove(par._p)

d.save('consent-templates.docx')
PY
# Page check. Verdana and Georgia may not be installed where this runs, and LibreOffice would then swap in a narrower
# face and undercount. The check copy names DejaVu Sans and DejaVu Serif, which are as wide or wider, so a pass here holds.
if command -v soffice >/dev/null 2>&1; then
  tmp=$(mktemp -d) && python3 - "$tmp" <<'PY'
import sys, zipfile
src, dst = zipfile.ZipFile('consent-templates.docx'), zipfile.ZipFile(sys.argv[1] + '/check.docx', 'w', zipfile.ZIP_DEFLATED)
for item in src.infolist():
    data = src.read(item.filename)
    if item.filename.endswith('.xml'):
        data = data.replace(b'"Verdana"', b'"DejaVu Sans"').replace(b'"Georgia"', b'"DejaVu Serif"')
    dst.writestr(item, data)
dst.close()
PY
  soffice --headless --convert-to pdf --outdir "$tmp" "$tmp/check.docx" >/dev/null 2>&1
  pages=$(pdfinfo "$tmp/check.pdf" 2>/dev/null | awk '/^Pages/{print $2}')
  if [ "$pages" = "9" ]; then echo "ok   consent-templates.docx  9 pages: cover, six forms, two survey screens"
  else echo "FAIL consent-templates.docx  $pages pages, expected 9: a form has run onto a second page"; exit 1; fi
else echo "note: LibreOffice is not installed, so the one-page check did not run"; fi
