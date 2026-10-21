from pathlib import Path
import hashlib, json, os, time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
RECORD = Path(__file__).resolve().parent
ops = []
def move(source, target):
    ops.append({'source': source, 'target': target})

move('01_课件', '01_课程资料/01_教师课件')
move('04_讲课视频', '01_课程资料/02_讲课视频')
move('08_平台资源下载/教师版PPT/05--通用输入输出GPIO-V2.1（教师版）-1.pptx', '01_课程资料/01_教师课件/05--通用输入输出GPIO-V2.1（教师版）-1.pptx')
move('08_平台资源下载/教师版PPT', '90_历史归档/重复资料/教师课件_平台下载副本')
move('08_平台资源下载/参考书（PDF格式）/ssreader5.7.2.25555超星阅读器.rar', '07_软件工具/01_安装包/ssreader5.7.2.25555超星阅读器.rar')
move('08_平台资源下载/参考书（PDF格式）', '01_课程资料/03_参考书')
move('08_平台资源下载/实验所用资料', '01_课程资料/04_芯片与板卡资料')
move('08_平台资源下载/复习用', '01_课程资料/05_复习资料')
for name in ['例子视频-GPIO流水灯-标准库STD法.wmv', '例子视频-GPIO流水灯-抽象库HAL法.wmv']:
    move('08_平台资源下载/练习例子工程/' + name, '01_课程资料/02_讲课视频/' + name)
move('08_平台资源下载/练习例子工程/8-配套例子题目和视频介绍二维码.pdf', '01_课程资料/06_例程说明/8-配套例子题目和视频介绍二维码.pdf')
move('08_平台资源下载/下载清单.md', '99_整理记录/此前记录/平台资源下载清单_2026-10-04.md')

move('02_作业_2026-09-19', '02_课程作业/作业1_2026-09-19')
for old, new in [('before_editorial_20261006', '20261006_文字调整前'), ('before_questions_20261006', '20261006_添加题目前'), ('before_fonts_20261006', '20261006_字体调整前')]:
    move('10_书面作业_作业2/_build/' + old, '90_历史归档/作业2/' + new)
move('10_书面作业_作业2', '02_课程作业/作业2')
move('09_课堂展示_时钟之迹/clock_traces_revision_20261006', '02_课程作业/时钟之迹/制作源文件')
for ext in ['pdf', 'pptx']:
    move('09_课堂展示_时钟之迹/时钟之迹_课堂展示_修订版.' + ext, '02_课程作业/时钟之迹/时钟之迹_课堂展示_修订版.' + ext)
    move('09_课堂展示_时钟之迹/时钟之迹_课堂展示.' + ext, '90_历史归档/时钟之迹/20261006_课堂展示初版/时钟之迹_课堂展示.' + ext)
move('09_课堂展示_时钟之迹/clock_traces_20261006', '90_历史归档/时钟之迹/20261006_课堂展示初版/制作源文件')

move('05_分析文档/审校资料', '90_历史归档/此前审校记录/审校资料')
move('05_分析文档', '03_学习笔记')
move('作业2与时钟之迹/讲课视频学习索引', '03_学习笔记/讲课视频学习索引')
move('作业2与时钟之迹/课程补充与版本对照', '03_学习笔记/课程补充与版本对照')

move('06_例程_时钟之迹/02_工程例程', '04_工程实践/01_时钟与SysTick/02_工程例程')
move('06_例程_时钟之迹/03_原始压缩包', '04_工程实践/01_时钟与SysTick/03_原始压缩包')
move('08_平台资源下载/练习例子工程', '04_工程实践/02_教师例程')
move('嵌入式作业/_archive_trash', '90_历史归档/过程日志/早期同步与核查')
move('嵌入式作业', '04_工程实践/03_环境与工程验证')
move('作业2与时钟之迹/代码与图件', '04_工程实践/04_补充代码包')

move('03_作业_2026-09-29', '90_历史归档/作业2/20260929_早期解答与资料')
move('06_例程_时钟之迹', '90_历史归档/时钟之迹/早期讨论稿与源文件')
move('作业2与时钟之迹', '90_历史归档/旧版汇总_作业2与时钟之迹')
move('历史版本_20261006整改前', '90_历史归档/此前审校记录/20261006_整改前备份')
for name in ['全宗整改实施记录_2026-10-06.md', '全宗整改宪章_2026-10-06.md', '全宗整改宪章_2026-10-06.pdf']:
    move(name, '90_历史归档/此前审校记录/' + name)
for name in ['all_pages.txt', 'docx_full_sequential.txt', 'docx_text_dump.txt', 'pdf_text_dump.txt']:
    move(name, '99_整理记录/此前文本提取/' + name)

def map_path(path):
    result = path
    for op in ops:
        if result == op['source'] or result.startswith(op['source'] + '/'):
            result = op['target'] + result[len(op['source']):]
    return result

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def project_refs(project):
    checks = []
    tree = ET.parse(project)
    for node in tree.findall('.//FilePath'):
        if node.text:
            checks.append(('source', node.text))
    for node in tree.findall('.//IncludePath'):
        for value in (node.text or '').split(';'):
            if value.strip(): checks.append(('include', value.strip()))
    rows = []
    for kind, value in sorted(set(checks)):
        if '$' in value: continue
        target = Path(value) if Path(value).is_absolute() else project.parent / value
        rows.append({'kind': kind, 'value': value, 'exists': target.exists()})
    return rows

if __name__ == '__main__':
    for op in ops:
        source, target = ROOT / op['source'], ROOT / op['target']
        assert source.exists(), source
        assert not target.exists(), target
        assert ROOT in source.resolve().parents and ROOT in target.resolve().parents
    paths = []
    for folder, dirs, files in os.walk(ROOT):
        if Path(folder) == ROOT: dirs[:] = [d for d in dirs if d != '99_整理记录']
        for name in files: paths.append(Path(folder) / name)
    rows = []
    started = time.monotonic()
    for i, path in enumerate(sorted(paths)):
        rel = path.relative_to(ROOT).as_posix()
        info = path.stat()
        rows.append({'before': rel, 'after': map_path(rel), 'bytes': info.st_size,
                     'sha256': digest(path), 'mtime_ns': info.st_mtime_ns})
        if (i + 1) % 4000 == 0: print(f'Inventoried {i + 1} files', flush=True)
    (RECORD / '移动计划.json').write_text(json.dumps(ops, ensure_ascii=False, indent=2), encoding='utf-8')
    (RECORD / '文件清单_整理前.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    project_data = {p.relative_to(ROOT).as_posix(): project_refs(p) for p in paths if p.suffix.lower() == '.uvprojx'}
    (RECORD / '工程依赖_整理前.json').write_text(json.dumps(project_data, ensure_ascii=False, indent=2), encoding='utf-8')
    missing = {p: [r for r in checks if not r['exists']] for p, checks in project_data.items()}
    missing = {p: v for p, v in missing.items() if v}
    print(json.dumps({'files': len(rows), 'bytes': sum(r['bytes'] for r in rows), 'moves': len(ops),
                      'projects': len(project_data), 'projects_with_existing_missing_refs': {p: len(v) for p, v in missing.items()},
                      'elapsed_seconds': round(time.monotonic() - started, 1)}, ensure_ascii=False), flush=True)
