#!/usr/bin/env python3
"""Make four print sheets and image sheets from the current LCEDA export."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import pymupdf as fitz

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'Verified图纸'
EDIT=DEST/'编辑源文件'
RAW=EDIT/'嘉立创原始导出.pdf'
NAMES=['01_最小系统原理图','02_实验电路图','03_主循环与中断流程图','04_按键消抖与RGB流程图']
project=json.loads((DEST/'Pandora_L496_Verified.json').read_text(encoding='utf-8-sig'))
assert project['title']=='Pandora_L496_Verified' and len(project['schematics'])==4
combined=fitz.open()
with fitz.open(RAW) as source:
    assert len(source)==4
    for i,(page,name) in enumerate(zip(source,NAMES)):
        svg=page.get_svg_image(text_as_path=True)
        (EDIT/f'{name}.svg').write_text(svg,encoding='utf-8')
        svgdoc=fitz.open('svg',svg.encode('utf-8'))
        vector=fitz.open('pdf',svgdoc.convert_to_pdf())
        single=fitz.open()
        out=single.new_page(width=1190.5511811,height=841.8897638)
        out.show_pdf_page(out.rect+(12,12,-12,-12),vector,0,keep_proportion=True)
        single.set_metadata({'title':name[3:],'author':'Peak','creator':'嘉立创EDA 6.5.51 / A3 vector print'})
        single.save(DEST/f'{name}.pdf',garbage=4,deflate=True)
        out.get_pixmap(dpi=300).save(DEST/f'{name}.png')
        out.get_pixmap(dpi=110).save(ROOT/f'logs/verified_final_{i+1}.png')
        combined.insert_pdf(single)
        data=project['schematics'][i]['dataStr']
        (EDIT/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        single.close();vector.close();svgdoc.close()
combined.set_metadata({'title':'Pandora_L496_Verified / 四页图纸','author':'Peak','creator':'嘉立创EDA 6.5.51 / A3 vector print'})
combined.save(DEST/'Verified_四页合订.pdf',garbage=4,deflate=True)
combined.close()
# Update the main deliverable paths, retaining an earlier copy in task logs.
for source,target in [
 (DEST/'Pandora_L496_Verified.json',ROOT/'hardware/lceda/Pandora_L496_嘉立创导出.json'),
 (EDIT/'嘉立创导出网表.net',ROOT/'hardware/lceda/Pandora_L496_嘉立创导出.net'),
 (RAW,ROOT/'hardware/lceda/嘉立创原始导出.pdf'),
 (DEST/'Verified_四页合订.pdf',ROOT/'output/pdf/潘多拉_嘉立创EDA_原理图与流程图.pdf')]:
    if target.exists():
        shutil.copy2(target,ROOT/'logs'/('before_verified_update_'+target.name))
    shutil.copy2(source,target)
print(str(DEST))
