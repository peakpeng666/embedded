from pathlib import Path
import json, time
from prepare_organization import ROOT, RECORD, map_path, digest, project_refs

inventory = json.loads((RECORD / '文件清单_整理前.json').read_text(encoding='utf-8'))
missing, changed = [], []
for i, row in enumerate(inventory):
    path = ROOT / row['after']
    if not path.is_file():
        missing.append(row['after'])
    elif digest(path) != row['sha256']:
        changed.append({'path': row['after'], 'old_bytes': row['bytes'], 'new_bytes': path.stat().st_size})
    if (i + 1) % 4000 == 0: print(f'Checked {i+1} files', flush=True)
before = json.loads((RECORD / '工程依赖_整理前.json').read_text(encoding='utf-8'))
new_missing, after = [], {}
for old, checks in before.items():
    new = map_path(old)
    now = project_refs(ROOT / new)
    after[new] = now
    lookup = {(r['kind'], r['value']): r['exists'] for r in checks}
    for r in now:
        if not r['exists'] and lookup.get((r['kind'], r['value']), True):
            new_missing.append({'project': new, **r})
(RECORD / '工程依赖_整理后.json').write_text(json.dumps(after, ensure_ascii=False, indent=2), encoding='utf-8')
result = {'files_checked': len(inventory), 'original_bytes': sum(r['bytes'] for r in inventory),
          'missing_files': missing, 'changed_files': changed, 'projects_checked': len(before),
          'new_missing_dependencies': new_missing}
(RECORD / '搬移核对结果.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False), flush=True)
