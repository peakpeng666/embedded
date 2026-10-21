"""Rebuild isolated copies using the installed Keil; preserve course originals."""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
WORK = Path(tempfile.mkdtemp(prefix="embedded_check_", dir=r"C:\Temp"))
UV4 = Path(r"C:\Keil_v5\UV4\UV4.exe")
JOBS = [
    ("spl_clock", ROOT / "04_工程实践/03_环境与工程验证/02_工程验证/01_标准库工程_5-STM32时钟系统", "Template.uvprojx"),
    ("cubemx_hal", ROOT / "04_工程实践/03_环境与工程验证/04_CubeMX工程/clock168_gpio", "MDK-ARM/clock168_gpio.uvprojx"),
]
results = []
for name, source, project_name in JOBS:
    dest = WORK / name
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns("Obj", "*.uvguix.*", "*.axf", "*.o", "*.crf", "*.d"))
    project = dest / project_name
    tree = ET.parse(project)
    for hook in ("BeforeCompile", "BeforeMake", "AfterMake"):
        for entry in tree.findall(f".//{hook}"):
            for n in (1, 2):
                if entry.findtext(f"RunUserProg{n}") == "1" and (entry.findtext(f"UserProg{n}Name") or "").strip():
                    raise RuntimeError(f"Unexpected enabled build hook in {name}: {hook}")
    rawlog = WORK / f"{name}.raw.log"
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    started = time.time()
    command = [str(UV4), "-r", str(project), "-j0", "-o", str(rawlog)]
    print(f"START {name}: {project}", flush=True)
    try:
        run = subprocess.run(command, cwd=dest, startupinfo=startup, timeout=120, capture_output=True)
        text = rawlog.read_bytes().decode("gb18030", errors="replace") if rawlog.exists() else "No build log was produced."
        (OUT / f"{name}_rebuild.log").write_text(text, encoding="utf-8")
        result = {"name": name, "source": str(source), "isolated_project": str(project), "exit_code": run.returncode,
                  "duration_seconds": round(time.time() - started, 1), "log": str(OUT / f"{name}_rebuild.log"),
                  "passed": "0 Error(s)" in text and run.returncode in (0, 1)}
        print(json.dumps(result, ensure_ascii=False), flush=True)
        print(text[-2500:], flush=True)
    except subprocess.TimeoutExpired:
        result = {"name": name, "passed": False, "error": "Timed out after 120 seconds"}
        print(json.dumps(result), flush=True)
    results.append(result)
    (OUT / "build_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Isolated working directory: {WORK}", flush=True)
