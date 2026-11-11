#!/bin/sh
# Rebuilds consent-templates.docx from consent-templates.md. Run from this folder.
pandoc -f markdown+hard_line_breaks consent-templates.md -o consent-templates.docx && python3 - <<'PY'
from docx import Document
from docx.shared import Pt, Inches, RGBColor
d = Document('consent-templates.docx')
for s in d.sections:
    s.top_margin = s.bottom_margin = Inches(0.8); s.left_margin = s.right_margin = Inches(0.95)
for st in d.styles:
    if st.type != 1: continue
    st.font.name = 'Calibri'
    if st.name in ('Normal', 'Body Text', 'First Paragraph', 'Compact'):
        st.font.size = Pt(11.5); st.paragraph_format.space_after = Pt(7); st.paragraph_format.space_before = Pt(0)
    if st.name in ('Heading 1', 'Title'):
        st.font.size = Pt(17); st.font.color.rgb = RGBColor(0x1c, 0x1b, 0x19)
        st.paragraph_format.space_before = Pt(0); st.paragraph_format.space_after = Pt(5)
d.save('consent-templates.docx')
PY
