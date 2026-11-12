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
    s.top_margin = s.bottom_margin = Inches(0.85); s.left_margin = s.right_margin = Inches(1.0)

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
        st.font.size = Pt(10); pf.space_after = Pt(6); pf.space_before = Pt(0); pf.line_spacing = 1.15
    if st.name == 'Heading 1':
        face(st, 'Georgia'); st.font.size = Pt(20); st.font.bold = True
        pf.space_before = Pt(0); pf.space_after = Pt(10); pf.keep_with_next = True; rule_below(st)
    if st.name == 'Title':
        face(st, 'Georgia'); st.font.size = Pt(28); st.font.bold = True
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT; pf.space_after = Pt(8); rule_below(st)
    if st.name == 'Subtitle':
        st.font.size = Pt(10); st.font.bold = True; st.font.color.rgb = BRASS
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT; pf.space_after = Pt(16)
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
  if [ "$pages" = "8" ]; then echo "ok   consent-templates.docx  8 pages: cover, six forms, survey screens"
  else echo "FAIL consent-templates.docx  $pages pages, expected 8: a form has run onto a second page"; exit 1; fi
else echo "note: LibreOffice is not installed, so the one-page check did not run"; fi
