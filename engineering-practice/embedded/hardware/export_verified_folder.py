#!/usr/bin/env python3
"""Make four print sheets and image sheets from the current LCEDA export."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import pymupdf as fitz

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'verified-drawings'
EDIT=DEST/'editable-sources'
RAW=EDIT/'lceda-original-export.pdf'
NAMES=['01_minimal-system-schematic','02_experiment-circuit','03_main-loop-and-interrupt-flowchart','04_button-debounce-and-rgb-flowchart']
required = [DEST/'Pandora_L496_Verified.json', RAW, EDIT/'lceda-export-netlist.net']
missing = [str(path) for path in required if not path.is_file()]
if missing:
    raise SystemExit('Missing verified drawing inputs:\n' + '\n'.join(missing))
project=json.loads((DEST/'Pandora_L496_Verified.json').read_text(encoding='utf-8-sig'))
if (not isinstance(project, dict) or project.get('title') != 'Pandora_L496_Verified'
        or not isinstance(project.get('schematics'), list)
        or len(project['schematics']) != 4
        or any(not isinstance(sheet, dict) or not isinstance(sheet.get('dataStr'), dict) for sheet in project['schematics'])):
    raise SystemExit('Invalid four-sheet verified project; outputs unchanged')
combined=fitz.open()
with fitz.open(RAW) as source:
    if len(source) != 4:
        raise SystemExit('Expected exactly four verified PDF pages; outputs unchanged')
    (ROOT/'logs').mkdir(parents=True, exist_ok=True)
    (ROOT/'output/pdf').mkdir(parents=True, exist_ok=True)
    (ROOT/'hardware/lceda').mkdir(parents=True, exist_ok=True)
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
combined.save(DEST/'Verified_four-page-bound-volume.pdf',garbage=4,deflate=True)
combined.close()
# Update the main deliverable paths, retaining an earlier copy in task logs.
for source,target in [
 (DEST/'Pandora_L496_Verified.json',ROOT/'hardware/lceda/Pandora_L496_lceda-export.json'),
 (EDIT/'lceda-export-netlist.net',ROOT/'hardware/lceda/Pandora_L496_lceda-export.net'),
 (RAW,ROOT/'hardware/lceda/lceda-original-export.pdf'),
 (DEST/'Verified_four-page-bound-volume.pdf',ROOT/'output/pdf/Pandora_lceda-EDA_schematic-and-flowcharts.pdf')]:
    if target.exists():
        shutil.copy2(target,ROOT/'logs'/('before_verified_update_'+target.name))
    shutil.copy2(source,target)
print(str(DEST))

