#!/usr/bin/env python3
"""Bundle only this task's source, official references and verified outputs."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PRACTICE=ROOT.parent
DEST=PRACTICE/'pandora-delivery'
VIDEO=PRACTICE/'keil-board-demos'
# Validate local-only evidence before modifying an existing delivery folder.
required_files = [
 ROOT/'output/pdf/Pandora_lceda-EDA_schematic-and-flowcharts.pdf',
 ROOT/'output/pdf/STM32L496_minimal-system-and-experiment-circuit_official-drawing.pdf',
 ROOT/'hardware/lceda/Pandora_L496_lceda-export.json',
 ROOT/'hardware/critical_review.md',
 ROOT/'hardware/lceda/verification-results.json',
 ROOT/'logs/windows_before_keil.json', ROOT/'logs/windows_after_keil.json',
 VIDEO/'Windows-multi-tool-board-demo.mp4',
 VIDEO/'Windows-multi-tool-board-demo.srt',
 VIDEO/'lceda-EDA-schematic-review-demo.mp4',
]
missing = [str(path) for path in required_files if not path.is_file()]
if not (ROOT/'hardware/sources').is_dir():
    missing.append(str(ROOT/'hardware/sources'))
if missing:
    raise SystemExit('Missing local handoff inputs; no delivery files were copied:\n' + '\n'.join(missing))
files=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT)
files=[ROOT/entry.decode('utf-8') for entry in files.split(b'\0') if entry]
missing_sources = [str(source) for source in files if not source.is_file()]
if missing_sources:
    raise SystemExit('Missing source snapshot inputs; delivery unchanged:\n' + '\n'.join(missing_sources))
DEST.mkdir(exist_ok=True)
for source in files:
    if source.is_file():
        target=DEST/'source-snapshot'/source.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
# References were deliberately excluded from Git, but belong in the local handoff.
shutil.copytree(ROOT/'hardware/sources',DEST/'source-snapshot/hardware/sources',dirs_exist_ok=True)
printdir=DEST/'source-snapshot/output/pdf'
printdir.mkdir(parents=True,exist_ok=True)
for name in ['Pandora_lceda-EDA_schematic-and-flowcharts.pdf','STM32L496_minimal-system-and-experiment-circuit_official-drawing.pdf']:
    shutil.copy2(ROOT/'output/pdf'/name,printdir/name)
for p in (ROOT/'output/pdf').glob('lceda_*_preview.png'):
    shutil.copy2(p,printdir/p.name)
top_files={
 ROOT/'output/pdf/Pandora_lceda-EDA_schematic-and-flowcharts.pdf':'Pandora_schematic-and-flowcharts_A3.pdf',
 ROOT/'hardware/lceda/Pandora_L496_lceda-export.json':'Pandora_lceda-EDA-native-project.json',
 ROOT/'hardware/critical_review.md':'sources-and-implementation-review.md',
 VIDEO/'Windows-multi-tool-board-demo.mp4':'Windows-multi-tool-board-demo.mp4',
 VIDEO/'Windows-multi-tool-board-demo.srt':'Windows-multi-tool-board-demo.srt',
 VIDEO/'lceda-EDA-schematic-review-demo.mp4':'lceda-EDA-schematic-review-demo.mp4',
}
for source,name in top_files.items():shutil.copy2(source,DEST/name)
evidence=DEST/'validation-records'
evidence.mkdir(exist_ok=True)
for name in ['windows_before_keil.json','windows_after_keil.json']:
    shutil.copy2(ROOT/'logs'/name,evidence/name)
shutil.copy2(ROOT/'hardware/lceda/verification-results.json',evidence/'EDA-netlist-and-pin-verification.json')
readme='''潘多拉 Windows 开发与专业图纸交付
日期：2026-10-21

录屏：
  Windows-multi-tool-board-demo.mp4：3分29秒，Keil、MobaXterm、CubeIDE、CubeMX、Proteus。
  lceda-EDA-schematic-review-demo.mp4：约44秒，检查四页原生图纸。

图纸：
  Pandora_schematic-and-flowcharts_A3.pdf：四页 A3，最小系统、实验电路、程序与中断、消抖与RGB状态机。
  Pandora_lceda-EDA-native-project.json：嘉立创EDA标准版“文件→打开→嘉立创EDA→导入”，可编辑。
  sources-and-implementation-review.md：原厂资料对照、引脚核对与实现说明。

源码：
  source-snapshot/keil/lab1.uvprojx：Keil AC5 工程，与 CubeIDE 共用 lab1/src 中的 C 源码。
  source-snapshot/keil/README.md：编译、下载、调试与串口操作。
  source-snapshot/hardware/README.md：图纸来源、打开方式与复核方法。
  source-snapshot/hardware/sources：官方资料、开发指南与引脚 XML。
  source-snapshot/hardware/lceda：应用保存副本、网表、原始 PDF、矢量 SVG 与核对结果。

实板：Keil 下载与校验通过，仅应用的两个 2 KiB 页改变，前 64 KiB 引导区不变。
工程地址 0x08010000；COM3，115200/8N1/无流控。
验证范围：编译、下载、调试、串口与图纸导出；PCB 丝印、BOOT 帽位和阻容值未在实物上测量。
'''
(DEST/'00_delivery-notes.txt').write_text(readme,encoding='utf-8-sig')
manifest={str(p.relative_to(DEST)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
          for p in sorted(DEST.rglob('*')) if p.is_file() and p.name!='file-checksums.json'}
(DEST/'file-checksums.json').write_text(json.dumps({'created_at':datetime.now().astimezone().isoformat(),'files':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
archive=PRACTICE/'Pandora_demos-and-drawings.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file():z.write(p,Path(DEST.name)/p.relative_to(DEST))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'folder':str(DEST),'archive':str(archive),'files':len(manifest)+1,'archive_bytes':archive.stat().st_size,
                  'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},ensure_ascii=False))

