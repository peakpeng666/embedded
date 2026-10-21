#!/usr/bin/env python3
"""Build the ARM application with native Windows/Linux Python; no hardware I/O."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toolchain-dir", type=Path, help="Directory containing arm-none-eabi-gcc[.exe]")
    args = parser.parse_args()
    compiler = None
    if args.toolchain_dir:
        compiler = args.toolchain_dir / ("arm-none-eabi-gcc.exe" if os.name == "nt" else "arm-none-eabi-gcc")
        if not compiler.is_file():
            parser.error(f"Compiler not found: {compiler}")
    elif shutil.which("arm-none-eabi-gcc"):
        compiler = Path(shutil.which("arm-none-eabi-gcc"))
    elif os.name != "nt":
        local = ROOT / ".toolchains/arm/usr/bin/arm-none-eabi-gcc"
        if local.is_file():
            compiler = local
    if compiler is None:
        parser.error("Install the Windows arm-none-eabi toolchain and add its bin directory to PATH, or pass --toolchain-dir.")
    suffix = ".exe" if compiler.name.endswith(".exe") else ""
    tool_dir = compiler.parent
    def tool(name):
        path = tool_dir / f"arm-none-eabi-{name}{suffix}"
        if not path.is_file():
            parser.error(f"Missing tool: {path}")
        return str(path)
    def run(command):
        print(subprocess.list2cmdline([str(x) for x in command]), flush=True)
        subprocess.run([str(x) for x in command], cwd=ROOT / "lab1", check=True)
    out = ROOT / "lab1/build"
    out.mkdir(parents=True, exist_ok=True)
    flags = ["-std=c11", "-mcpu=cortex-m4", "-mthumb", "-mfloat-abi=soft", "-Os", "-g3",
             "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections",
             "-Wall", "-Wextra", "-Werror", "-Isrc", "-Ivendor/st", "-Ivendor/arm"]
    objects = []
    for source in ["startup.S", "main.c", "lab_logic.c", "runtime.c"]:
        obj = out / (Path(source).stem + ".o")
        run([tool("gcc"), *flags, "-c", "src/" + source, "-o", obj])
        objects.append(obj)
    elf = out / "lab1.elf"
    run([tool("gcc"), "-mcpu=cortex-m4", "-mthumb", "-mfloat-abi=soft", "-nostdlib",
         "-Tstm32l496_app.ld", "-Wl,--gc-sections,-Map,build/lab1.map", *objects, "-lgcc", "-o", elf])
    for fmt, name in [("binary", "lab1.bin"), ("ihex", "lab1.hex")]:
        run([tool("objcopy"), "-O", fmt, elf, out / name])
    run([tool("size"), elf])
    print("BIN SHA256:", hashlib.sha256((out / "lab1.bin").read_bytes()).hexdigest())
    print("Build only. The tested firmware/ release files are not replaced.")


if __name__ == "__main__":
    main()
