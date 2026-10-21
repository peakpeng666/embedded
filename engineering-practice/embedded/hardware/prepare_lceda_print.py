#!/usr/bin/env python3
"""Preserve LCEDA-exported vector content; make portable A3 print copies.

The EDA app's original PDF is preserved. This step changes page size and turns
font glyphs into vector paths; it does not redraw or alter circuit connectivity.
"""
from pathlib import Path
import pymupdf as fitz

ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'hardware/lceda/lceda-original-export.pdf'
dest=ROOT/'output/pdf/Pandora_lceda-EDA_schematic-and-flowcharts.pdf'
out=fitz.open()
with fitz.open(src) as doc:
    assert len(doc)==4
    for i,page in enumerate(doc,1):
        svg=page.get_svg_image(text_as_path=True)
        # Store app-rendered outlines, so Chinese fonts travel with the print file.
        (ROOT/f'hardware/lceda/{i:02d}_lceda-export.svg').write_text(svg,encoding='utf-8')
        converted=fitz.open('svg',svg.encode('utf-8'))
        vector=fitz.open('pdf',converted.convert_to_pdf())
        p=out.new_page(width=1190.5511811,height=841.8897638)
        p.show_pdf_page(p.rect+ (12,12,-12,-12),vector,0,keep_proportion=True)
out.set_metadata({'title':'正点原子潘多拉：最小系统、实验电路与程序流程图','author':'Peak / 嘉立创 EDA 标准版',
                  'subject':'依据官方 V3.4 电路与 lab1 实现核对；四页 A3；原生工程另附',
                  'creator':'嘉立创 EDA 标准版 6.5.51；A3 排版与文字轮廓转换：PyMuPDF'})
out.save(dest,garbage=4,deflate=True)
out.close()
with fitz.open(dest) as doc:
    for i,page in enumerate(doc,1):
        page.get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(ROOT/f'output/pdf/lceda_{i:02d}_preview.png')
print(str(dest))
