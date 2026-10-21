from pathlib import Path
from urllib.parse import unquote, quote
import json, os, re, shutil, stat, csv, ast
from prepare_organization import ROOT, RECORD, map_path, digest

inventory = json.loads((RECORD / '文件清单_整理前.json').read_text(encoding='utf-8'))
original = {row['after']: row for row in inventory}
changes = []

def save(relative, content):
    path = ROOT / relative
    data = content.encode('utf-8')
    if path.exists() and path.read_bytes() == data: return
    before_hash = None
    backup_rel = None
    if path.exists():
        backup = RECORD / '修改前' / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists(): shutil.copy2(path, backup)
        backup_rel = backup.relative_to(ROOT).as_posix()
        before_hash = digest(backup)
        if not (path.stat().st_mode & stat.S_IWRITE): path.chmod(path.stat().st_mode | stat.S_IWRITE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    changes.append({'path': relative, 'backup': backup_rel, 'before_sha256': before_hash, 'after_sha256': digest(path)})

active = ('01_课程资料/', '02_课程作业/', '03_学习笔记/', '04_工程实践/', '07_软件工具/')
links_fixed = 0
for row in inventory:
    current = row['after']
    if not current.endswith('.md') or not current.startswith(active): continue
    if '/node_modules/' in current or '/STM32CubeMX-6.18.1/' in current: continue
    path = ROOT / current
    old_path = ROOT / row['before']
    original_copy = RECORD / '修改前' / current
    try:
        text = (original_copy if original_copy.exists() else path).read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:
        continue
    def relink(match):
        global links_fixed
        value = match.group(1)
        if re.match(r'^(?:[a-zA-Z][a-zA-Z\d+.-]*:|#|//)', value): return match.group(0)
        plain = value.strip('<>')
        target_text, sep, fragment = plain.partition('#')
        target = (old_path.parent / unquote(target_text)).resolve()
        try: rel = target.relative_to(ROOT).as_posix()
        except ValueError: return match.group(0)
        mapped = ROOT / map_path(rel)
        if not mapped.exists(): return match.group(0)
        new = os.path.relpath(mapped, path.parent).replace('\\', '/')
        if target_text.endswith('/') and not new.endswith('/'): new += '/'
        new = new.replace(' ', '%20')
        if sep: new += '#' + fragment
        if new == plain: return match.group(0)
        links_fixed += 1
        return match.group(0).replace(value, new)
    text = re.sub(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', relink, text)
    if text != path.read_text(encoding='utf-8-sig'): save(current, text)

def replace(relative, pairs):
    path = ROOT / relative
    text = path.read_text(encoding='utf-8-sig')
    for old, new in pairs:
        assert old in text, (relative, old)
        text = text.replace(old, new)
    save(relative, text)

replace('02_课程作业/作业2/_build/prepare_projects.py', [
    ("ROOT = Path(r'D:\\Peak\\Desktop\\嵌入式')", 'ROOT = Path(__file__).resolve().parents[3]'),
    ("OUT = ROOT / '10_书面作业_作业2'", 'OUT = Path(__file__).resolve().parents[1]'),
    ("ROOT / '03_作业_2026-09-29'", "ROOT / '90_历史归档/作业2/20260929_早期解答与资料'"),
    ("ROOT / '嵌入式作业/", "ROOT / '04_工程实践/03_环境与工程验证/")])
replace('04_工程实践/03_环境与工程验证/01_环境检查/软件核查_20261006/verify_builds.py', [
    ('ROOT = Path(r"D:\\Peak\\Desktop\\嵌入式")', 'ROOT = Path(__file__).resolve().parents[4]'),
    ('ROOT / "嵌入式作业/', 'ROOT / "04_工程实践/03_环境与工程验证/')])
replace('04_工程实践/03_环境与工程验证/04_CubeMX工程/gen_script.txt', [
    ('D:/Peak/Desktop/嵌入式作业/04_CubeMX工程/clock168_gpio.ioc',
     (ROOT / '04_工程实践/03_环境与工程验证/04_CubeMX工程/clock168_gpio/clock168_gpio.ioc').as_posix())])
replace('02_课程作业/时钟之迹/制作源文件/sources/source_index.md', [
    ('D:\\Peak\\Desktop\\嵌入式\\08_平台资源下载\\练习例子工程',
     str(ROOT / '04_工程实践/02_教师例程'))])
replace('07_软件工具/03_辅助记录/装包与验证.py', [
    ('import os, sys, shutil, zipfile, glob, subprocess', 'import os, sys, shutil, zipfile, glob, subprocess\nfrom pathlib import Path'),
    ('KEIL = r"D:\\Keil_v5"', 'KEIL = r"C:\\Keil_v5"'),
    ('PACKS = r"D:\\Peak\\Desktop\\嵌入式\\07_软件工具"', 'PACKS = str(Path(__file__).resolve().parents[1] / "01_安装包")'),
    ('PROJ = r"D:\\Peak\\Desktop\\嵌入式\\06_例程_时钟之迹\\02_工程例程\\5-STM32时钟系统"',
     'PROJ = str(Path(__file__).resolve().parents[2] / "04_工程实践/01_时钟与SysTick/02_工程例程/5-STM32时钟系统")')])
replace('07_软件工具/README_老师作业_时钟之迹.txt', [
    ('D:\\Peak\\Desktop\\嵌入式\\06_例程_时钟之迹', str(ROOT / '04_工程实践/01_时钟与SysTick'))])

save('README.md', '''# 嵌入式课程文件

整理日期：2026-10-06

## 常用文件

| 内容 | 文件 |
| --- | --- |
| 作业 2 | [Word](02_课程作业/作业2/作业2_书面解答.docx) · [PDF](02_课程作业/作业2/作业2_书面解答.pdf) |
| 时钟之迹 | [课堂 PPT](02_课程作业/时钟之迹/时钟之迹_课堂展示_修订版.pptx) · [PDF](02_课程作业/时钟之迹/时钟之迹_课堂展示_修订版.pdf) |
| GPIO 工程与资料 | [工程目录](02_课程作业/作业2/GPIO工程/) · [打包文件](02_课程作业/作业2/作业2_工程与参考资料.zip) |
| 作业 1 | [文件夹](02_课程作业/作业1_2026-09-19/) |
| 复习 | [第 1–4 章知识与复习重点](03_学习笔记/课程知识与复习重点_第1-4章.md) |

在资源管理器里，也可以直接打开 `00_常用入口` 中的快捷方式。

## 目录

| 文件夹 | 内容 |
| --- | --- |
| [00_常用入口](00_常用入口/) | 常用作业、PPT、GPIO 工程和开发软件的快捷方式 |
| [01_课程资料](01_课程资料/) | 第 1–5 章课件、5 段视频、参考书、手册和实验说明 |
| [02_课程作业](02_课程作业/) | 作业 1、作业 2、时钟之迹，以及各自的配套文件 |
| [03_学习笔记](03_学习笔记/) | 复习提纲、开发板分析、视频索引和课程补充 |
| [04_工程实践](04_工程实践/) | 时钟、SysTick、教师例程、CubeMX 工程与验证记录 |
| [07_软件工具](07_软件工具/) | CubeMX、安装包、芯片包和标准外设库 |
| [90_历史归档](90_历史归档/) | 旧作业、旧 PPT、修改前备份、重复课件和此前审校记录 |
| [99_整理记录](99_整理记录/) | 路径对照、文件校验、整理前说明和文本提取记录 |

作业 2 采用宋体正文、黑体标题、Times New Roman 英文及数字、Consolas 代码。每道题前保留完整题目。

软件目录沿用 `07_软件工具`，CubeMX 的安装路径和原桌面快捷方式保持一致。新下载的课程文件放入 `01_课程资料`，新工程放入 `04_工程实践`，旧成品放入 `90_历史归档`。
''')

save('01_课程资料/README.md', '''# 课程资料

| 目录 | 内容 |
| --- | --- |
| [01_教师课件](01_教师课件/) | 第 1–5 章教师版 PPT；前四章的页码索引见课件引用映射表 |
| [02_讲课视频](02_讲课视频/) | 标准库建工程、CubeMX 建工程、汇编演示和两段 GPIO 流水灯视频 |
| [03_参考书](03_参考书/) | 课程参考书与 C/C++ 资料 |
| [04_芯片与板卡资料](04_芯片与板卡资料/) | STM32F4 和 Cortex-M4 手册 |
| [05_复习资料](05_复习资料/) | SysTick 相关课件摘页 |
| [06_例程说明](06_例程说明/) | 例题与配套视频说明 |

[F407、L496 数据手册及普中原理图](../02_课程作业/作业2/参考资料/)随作业 2 一起存放。[教师工程](../04_工程实践/02_教师例程/)归入工程实践。

PDZ 文件对应的超星阅读器压缩包位于[软件安装包](../07_软件工具/01_安装包/)。
''')

save('02_课程作业/README.md', '''# 课程作业

- [作业 1（2026-09-19）](作业1_2026-09-19/)：题目、解答和参考图件。
- [作业 2](作业2/)：本次完成的 Word、PDF、GPIO 工程和参考资料。
- [时钟之迹](时钟之迹/)：课堂展示修订版 PPT、PDF 和制作源文件。

旧稿集中存放在[历史归档](../90_历史归档/)。
''')

save('02_课程作业/作业2/README.md', '''# 作业 2

- [Word 编辑版](作业2_书面解答.docx)
- [PDF 阅读版](作业2_书面解答.pdf)
- [工程与参考资料 ZIP](作业2_工程与参考资料.zip)

## 配套文件

| 目录 | 内容 |
| --- | --- |
| [GPIO工程](GPIO工程/) | SPL、HAL 两种 GPIO 工程及空白模板；用 Keil 打开 `.uvprojx` |
| [参考资料](参考资料/) | F407、L496 数据手册和普中开发板原理图 |
| [配图](配图/) | 正文使用的 7 张图 |
| `_build` | 文档与配图生成脚本、页面预览、校验记录 |

正文共 12 页，包含原题、解答、真实代码和参考资料。代码及图件与正文一起保存在本目录。

文字调整前、添加题目前、字体调整前的文件位于[作业 2 历史版本](../../90_历史归档/作业2/)。
''')

save('02_课程作业/时钟之迹/README.md', '''# 时钟之迹

- [课堂 PPT：修订版](时钟之迹_课堂展示_修订版.pptx)
- [PDF 预览](时钟之迹_课堂展示_修订版.pdf)
- [演讲备注](制作源文件/notes/total.md)
- [源码引用索引](制作源文件/sources/source_index.md)

`制作源文件` 保存 SVG、备注、源码摘录和版面检查文件；完整教师工程位于[工程实践](../../04_工程实践/02_教师例程/)。

初版演示稿和早期讨论稿放在[时钟之迹历史版本](../../90_历史归档/时钟之迹/)。
''')

save('03_学习笔记/README.md', '''# 学习笔记

- [课程知识与复习重点：第 1–4 章](课程知识与复习重点_第1-4章.md)
- [课堂入门：开发板与读图](课堂入门_开发板与读图.md)
- [F407 硬件与原理图分析](STM32F407ZGT6硬件平台架构与原理图电气分析指南.md)
- [F407 开发板详解](F407开发板详解_对照官方手册.md)
- [时钟及前置章节笔记](综合分析_设置时钟及前置章节.md)
- [讲课视频学习索引 PDF](讲课视频学习索引/讲课视频学习索引.pdf)
- [课程补充与版本对照 PDF](课程补充与版本对照/课程补充与版本对照.pdf)

视频索引和课程补充的源文件压缩包保存在各自目录；课程补充的 Word 留存较早版本，阅读入口使用 PDF。

这些笔记保留了当时的课程记录与分析。当前作业文件见[课程作业](../02_课程作业/)，当前目录位置以根目录说明为准。
''')

save('04_工程实践/README.md', '''# 工程实践

| 目录 | 内容 |
| --- | --- |
| [01_时钟与SysTick](01_时钟与SysTick/) | 时钟配置、SysTick、LED 和标准库模板，以及原始压缩包 |
| [02_教师例程](02_教师例程/) | CH5EX01HAL、CH5Ex01STD 与其他章节的例程压缩包 |
| [03_环境与工程验证](03_环境与工程验证/) | 软件检查、工程编译记录、调试截图和 CubeMX 工程 |
| [04_补充代码包](04_补充代码包/) | 之前整理的 HAL/SPL 示例、教师例程修订包和图件 |

作业 2 的 [GPIO 工程](../02_课程作业/作业2/GPIO工程/)随报告保存在一起，可从本目录的快捷方式进入。

打开 Keil 工程时选择 `.uvprojx`。工程内部的源码、头文件、库文件和编译输出保留在原有层级。
''')

save('04_工程实践/01_时钟与SysTick/README.md', '''# 时钟与 SysTick 例程

| 工程 | 打开文件 |
| --- | --- |
| 时钟系统 | [5-STM32时钟系统/Template.uvprojx](02_工程例程/5-STM32时钟系统/Template.uvprojx) |
| SysTick | [7-SysTick系统定时器/Template.uvprojx](02_工程例程/7-SysTick系统定时器/Template.uvprojx) |
| 标准库模板 | [STD_模板/Template.uvprojx](02_工程例程/STD_模板/Template.uvprojx) |
| LED | [STD_LED/Template.uvprojx](02_工程例程/STD_LED/Template.uvprojx) |

[原始压缩包](03_原始压缩包/)保存解压前的文件。课堂演示稿见[时钟之迹](../../02_课程作业/时钟之迹/)。
''')

save('04_工程实践/02_教师例程/README.md', '''# 教师例程

- [HAL 工程](CH5EX01HAL/CH5EX01HAL/MDK-ARM/CH5EX01HAL.uvprojx)
- [标准外设库工程](CH5Ex01STD/UserMain/CH5EX01STD.uvprojx)
- 其他章节例程保留为原始 RAR / ZIP，按需解压使用。

流水灯演示视频位于[课程视频](../../01_课程资料/02_讲课视频/)，例题与视频说明位于[例程说明](../../01_课程资料/06_例程说明/)。
''')

save('07_软件工具/README.md', '''# 软件工具

| 位置 | 内容 |
| --- | --- |
| `STM32CubeMX-6.18.1/MX/` | 已配置的 CubeMX 程序；从桌面或常用入口中的快捷方式启动 |
| [01_安装包](01_安装包/) | MDK、CubeMX 安装包、CMSIS/DFP 芯片包、超星阅读器压缩包 |
| [02_开发库](02_开发库/) | STM32F4 标准外设库及其压缩包 |
| [03_辅助记录](03_辅助记录/) | 安装过程脚本和截图 |

Keil 位于 `C:\\Keil_v5`。软件快捷方式见[常用入口](../00_常用入口/)，已有的软件检查记录见[环境与工程验证](../04_工程实践/03_环境与工程验证/01_环境检查/)。
''')

save('90_历史归档/README.md', '''# 历史归档

| 目录 | 内容 |
| --- | --- |
| [作业2](作业2/) | 9 月 29 日早期解答，以及 10 月 6 日三次修改前的备份 |
| [时钟之迹](时钟之迹/) | 早期讨论稿与课堂展示初版，包含制作文件 |
| [旧版汇总_作业2与时钟之迹](旧版汇总_作业2与时钟之迹/) | 之前汇总的作业、讲稿、PPT 和整包文件 |
| [重复资料](重复资料/) | 已核对内容相同的四份教师课件副本 |
| [此前审校记录](此前审校记录/) | 此前整改文档、审校资料和修改前备份 |
| [过程日志](过程日志/) | 早期同步和核查日志 |

当前作业与展示稿在[课程作业](../02_课程作业/)。归档文件保留原文，其中的旧路径和旧提交说明对应当时版本。
''')

save('99_整理记录/README.md', '''# 整理记录

- [本次整理说明](2026-10-06/整理说明.md)
- [目录移动对照 CSV](2026-10-06/目录移动对照.csv)
- `2026-10-06/文件清单_整理前.json`：17,610 个原文件的原位置、新位置、字节数和 SHA-256。
- `2026-10-06/修改前/`：更新目录说明和路径引用前的原文件。
- `此前记录/`：原平台下载清单。
- `此前文本提取/`：此前从 Word、PDF 提取的文本。
''')

ops = json.loads((RECORD / '移动计划.json').read_text(encoding='utf-8'))
with (RECORD / '目录移动对照.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['原位置', '新位置'])
    writer.writerows((r['source'], r['target']) for r in ops)

for row in changes:
    if row['path'].endswith('.py'): ast.parse((ROOT / row['path']).read_text(encoding='utf-8'))
known = {r['path'] for r in changes}
for backup in (RECORD / '修改前').rglob('*'):
    if not backup.is_file(): continue
    relative = backup.relative_to(RECORD / '修改前').as_posix()
    if relative not in known:
        changes.append({'path': relative, 'backup': backup.relative_to(ROOT).as_posix(),
                        'before_sha256': digest(backup), 'after_sha256': digest(ROOT / relative)})
(RECORD / '说明与路径修改.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'links_updated': links_fixed, 'files_updated_or_created': len(changes)}, ensure_ascii=False))
