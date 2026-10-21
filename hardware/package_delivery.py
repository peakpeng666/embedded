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
DEST=PRACTICE/'潘多拉开发交付'
DEST.mkdir(exist_ok=True)
VIDEO=PRACTICE/'Keil连板演示'
files=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT)
files=[ROOT/entry.decode('utf-8') for entry in files.split(b'\0') if entry]
for source in files:
    if source.is_file():
        target=DEST/'工程源码'/source.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
# References were deliberately excluded from Git, but belong in the local handoff.
shutil.copytree(ROOT/'hardware/sources',DEST/'工程源码/hardware/sources',dirs_exist_ok=True)
printdir=DEST/'工程源码/output/pdf'
printdir.mkdir(parents=True,exist_ok=True)
for name in ['潘多拉_嘉立创EDA_原理图与流程图.pdf','STM32L496_最小系统与实验电路_官方图版.pdf']:
    shutil.copy2(ROOT/'output/pdf'/name,printdir/name)
for p in (ROOT/'output/pdf').glob('嘉立创_*_预览.png'):
    shutil.copy2(p,printdir/p.name)
top_files={
 ROOT/'output/pdf/潘多拉_嘉立创EDA_原理图与流程图.pdf':'潘多拉_原理图与流程图_A3.pdf',
 ROOT/'hardware/lceda/Pandora_L496_嘉立创导出.json':'潘多拉_嘉立创EDA原生工程.json',
 ROOT/'hardware/critical_review.md':'来源与实现核对.md',
 VIDEO/'Windows多软件连板开发演示.mp4':'Windows多软件连板开发演示.mp4',
 VIDEO/'Windows多软件连板开发演示.srt':'Windows多软件连板开发演示.srt',
 VIDEO/'嘉立创EDA图纸检查演示.mp4':'嘉立创EDA图纸检查演示.mp4',
}
for source,name in top_files.items():shutil.copy2(source,DEST/name)
evidence=DEST/'验证记录'
evidence.mkdir(exist_ok=True)
for name in ['windows_before_keil.json','windows_after_keil.json']:
    shutil.copy2(ROOT/'logs'/name,evidence/name)
shutil.copy2(ROOT/'hardware/lceda/核对结果.json',evidence/'EDA网表与引脚核对.json')
readme='''潘多拉 Windows 开发与专业图纸交付
日期：2026-10-21

先看两个实际录屏：
  Windows多软件连板开发演示.mp4：3分29秒，Keil、MobaXterm、CubeIDE、CubeMX、Proteus。
  嘉立创EDA图纸检查演示.mp4：约44秒，在本机专业软件中检查四页原生图纸。

图纸：
  潘多拉_原理图与流程图_A3.pdf：四页 A3，最小系统、实验电路、程序与中断、消抖与RGB状态机。
  潘多拉_嘉立创EDA原生工程.json：嘉立创EDA标准版“文件→打开→嘉立创EDA→导入”，可编辑。
  来源与实现核对.md：原厂资料冲突、代码依据、已验证项目和未核验实物信息。

源码：
  工程源码/keil/lab1.uvprojx：Keil AC5 工程，和 CubeIDE 共用 lab1/src 中的 C 源码。
  工程源码/keil/README.md：本机按键、编译、下载、调试、串口操作说明。
  工程源码/hardware/README.md：图纸的官方来源、打开方式、复核方法。
  工程源码/hardware/sources：完整官方原始资料、开发指南、ST资料与精确引脚XML。
  工程源码/hardware/lceda：应用保存副本、实际网表、原始PDF、矢量SVG和核对结果。

实板 Keil 下载与校验成功；仅应用的两个2KiB页改变，前64KiB引导区保持不变。
工程地址0x08010000。COM3，115200/8N1/无流控。不要将程序错误地覆盖到引导区。
本轮未新增实体按键实测；视频中调试器改变量是写RAM。Proteus场景为既有F401例程。
未确认PCB丝印版本、BOOT帽位与实际阻容测量值；原图U3型号、VREF旁注冲突均已注明。

原仓库：https://github.com/peakpeng666/embedded ，基线 fc4308a；此次改动保留在本机，未推送。
此包为现有板的实验摘绘与代码交付，不是已完成封装布局和生产验证的新PCB设计。
'''
(DEST/'00_交付说明.txt').write_text(readme,encoding='utf-8-sig')
manifest={str(p.relative_to(DEST)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
          for p in sorted(DEST.rglob('*')) if p.is_file() and p.name!='文件校验清单.json'}
(DEST/'文件校验清单.json').write_text(json.dumps({'created_at':datetime.now().astimezone().isoformat(),'files':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
archive=PRACTICE/'潘多拉_开发演示与专业图纸.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file():z.write(p,Path(DEST.name)/p.relative_to(DEST))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'folder':str(DEST),'archive':str(archive),'files':len(manifest)+1,'archive_bytes':archive.stat().st_size,
                  'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},ensure_ascii=False))
