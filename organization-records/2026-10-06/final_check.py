from pathlib import Path
from urllib.parse import unquote
import ast, hashlib, json, os, re, shutil, stat, zipfile
from prepare_organization import ROOT, RECORD, digest, project_refs, map_path

changes_path = RECORD / '说明与路径修改.json'
changes = json.loads(changes_path.read_text(encoding='utf-8'))
by_path = {row['path']: row for row in changes}

def update(relative, transform):
    path = ROOT / relative
    text = path.read_text(encoding='utf-8-sig')
    revised = transform(text)
    if revised == text: return
    if relative not in by_path:
        backup = RECORD / '修改前' / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
        row = {'path': relative, 'backup': backup.relative_to(ROOT).as_posix(), 'before_sha256': digest(backup)}
        changes.append(row)
        by_path[relative] = row
    path.chmod(path.stat().st_mode | stat.S_IWRITE)
    path.write_text(revised, encoding='utf-8', newline='')
    by_path[relative]['after_sha256'] = digest(path)

def update_clock_note(text):
    text = re.sub(r'1\. \*\*作业2\*\*[^\n]*',
                  '1. **作业2** —— [Word、PDF 与配套工程](../02_课程作业/作业2/)；', text, count=1)
    if '### 3.2 本地已归档' not in text: return text
    a = text.index('### 3.2 本地已归档')
    b = text.index('\n---', a)
    section = '''### 3.2 本地目录（2026-10-06 更新）

- [课程资料](../01_课程资料/)：课件、视频、参考书和手册。
- [课程作业](../02_课程作业/)：作业 1、作业 2、时钟之迹。
- [工程实践](../04_工程实践/)：完整例程与验证工程。
- 当前笔记与复习提纲保存在本目录。
'''
    return text[:a] + section + text[b:]

update('03_学习笔记/综合分析_设置时钟及前置章节.md', update_clock_note)
update('03_学习笔记/课程平台资源清单.md', lambda s: s.replace('01_课件\\', '01_课程资料\\01_教师课件\\').replace('04_讲课视频\\', '01_课程资料\\02_讲课视频\\'))
update('03_学习笔记/STM32F407ZGT6硬件平台架构与原理图电气分析指南.md', lambda s: s.replace('保留于原目录（05_分析文档）', '保留于本目录（03_学习笔记）'))
update('03_学习笔记/课程知识与复习重点_第1-4章.md', lambda s: s.replace('[第二次作业解答]', '[第二次作业早期解答]').replace('第二次作业解答存在下表所列问题，复习时请结合更正阅读。', '早期解答存在下表所列问题；[当前作业 2](../02_课程作业/作业2/)已另行整理。'))
changes_path.write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')

inventory = json.loads((RECORD / '文件清单_整理前.json').read_text(encoding='utf-8'))
preservation_errors = []
runtime_log_appends = []
for row in inventory:
    path = ROOT / row['after']
    if not path.exists():
        preservation_errors.append({'path': row['after'], 'error': 'missing'})
        continue
    if row['after'] in by_path:
        change = by_path[row['after']]
        if not change['backup'] or digest(ROOT / change['backup']) != row['sha256']:
            preservation_errors.append({'path': row['after'], 'error': 'original backup mismatch'})
    elif path.stat().st_size != row['bytes']:
        if row['after'].endswith('/validation/workflow.log') and path.stat().st_size >= row['bytes']:
            with path.open('rb') as f: original_prefix = f.read(row['bytes'])
            if hashlib.sha256(original_prefix).hexdigest() == row['sha256']:
                backup = RECORD / '预览服务日志快照' / row['before']
                backup.parent.mkdir(parents=True, exist_ok=True)
                if not backup.exists(): backup.write_bytes(original_prefix)
                runtime_log_appends.append({'path': row['after'], 'original_content_preserved': True,
                                            'added_bytes': path.stat().st_size - row['bytes']})
                continue
        preservation_errors.append({'path': row['after'], 'error': 'unexpected byte count change'})

changed_file_errors = []
for row in changes:
    if digest(ROOT / row['path']) != row['after_sha256']:
        changed_file_errors.append(row['path'])
    if row['path'].endswith('.py'):
        ast.parse((ROOT / row['path']).read_text(encoding='utf-8'))

docs = [ROOT / r['path'] for r in changes if r['path'].endswith('.md')]
broken_links, checked_links = [], 0
for doc in docs:
    for match in re.finditer(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', doc.read_text(encoding='utf-8-sig')):
        link = match.group(1).strip('<>')
        if re.match(r'^(?:[a-zA-Z][a-zA-Z\d+.-]*:|#|//)', link): continue
        link = unquote(link.split('#', 1)[0])
        checked_links += 1
        if not (doc.parent / link).exists():
            broken_links.append({'document': doc.relative_to(ROOT).as_posix(), 'link': link})

deliverables = []
for rel in [
    '02_课程作业/作业2/作业2_书面解答.docx',
    '02_课程作业/作业2/作业2_书面解答.pdf',
    '02_课程作业/作业2/作业2_工程与参考资料.zip',
    '02_课程作业/时钟之迹/时钟之迹_课堂展示_修订版.pptx',
    '02_课程作业/时钟之迹/时钟之迹_课堂展示_修订版.pdf',
]:
    row = next(r for r in inventory if r['after'] == rel)
    path = ROOT / rel
    same = digest(path) == row['sha256']
    if path.suffix in ['.docx', '.pptx', '.zip']:
        with zipfile.ZipFile(path) as z: assert z.testzip() is None, rel
    deliverables.append({'path': rel, 'unchanged': same})

generation_script = ROOT / '04_工程实践/03_环境与工程验证/04_CubeMX工程/gen_script.txt'
generation_target = generation_script.read_text(encoding='utf-8').splitlines()[0].removeprefix('config load ')
assert Path(generation_target).exists(), generation_target

baseline = json.loads((RECORD / '工程依赖_整理前.json').read_text(encoding='utf-8'))
new_missing = []
for old, checks in baseline.items():
    now = project_refs(ROOT / map_path(old))
    previous = {(r['kind'], r['value']): r['exists'] for r in checks}
    for r in now:
        if not r['exists'] and previous.get((r['kind'], r['value']), True):
            new_missing.append({'project': map_path(old), **r})

summary = {'original_files_preserved': len(inventory), 'preservation_errors': preservation_errors,
           'preview_service_log_appends': runtime_log_appends,
           'changed_file_errors': changed_file_errors, 'links_checked': checked_links, 'broken_links': broken_links,
           'deliverables': deliverables, 'projects_checked': len(baseline), 'new_missing_dependencies': new_missing,
           'cubemx_generation_target_exists': True,
           'root_directories': sorted(p.name for p in ROOT.iterdir() if p.is_dir())}
(RECORD / '最终检查结果.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False), flush=True)
