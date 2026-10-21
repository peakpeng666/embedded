#!/usr/bin/env python3
"""Build this project with the GNU Arm tools already bundled in CubeIDE."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
search_roots = [Path(os.environ.get("STM32CUBEIDE_HOME", "C:/ST"))]
candidates = []
for base in search_roots:
    candidates.extend(base.glob("STM32CubeIDE*/STM32CubeIDE/plugins/com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32*/tools/bin/arm-none-eabi-gcc.exe"))
    candidates.extend(base.glob("plugins/com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32*/tools/bin/arm-none-eabi-gcc.exe"))
if not candidates:
    raise SystemExit("CubeIDE GNU Arm tools not found. Set STM32CUBEIDE_HOME to the installation folder.")
compiler = sorted(candidates)[-1]
print("Using CubeIDE toolchain:", compiler.parent, flush=True)
subprocess.run([sys.executable, str(ROOT / "tools/build_firmware.py"),
                "--toolchain-dir", str(compiler.parent)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / "lab1/verify_image.py")], cwd=ROOT, check=True)
