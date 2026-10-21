# -*- coding: utf-8 -*-
"""Keil 装好后的收尾：导入 DFP/CMSIS pack + 命令行编译 T100 例程验证工具链"""
import os, sys, shutil, zipfile, glob, subprocess

KEIL = r"D:\Keil_v5"
UV4 = os.path.join(KEIL, "UV4", "UV4.exe")
PACKS = r"D:\Peak\Desktop\嵌入式\07_软件工具"
PROJ = r"D:\Peak\Desktop\嵌入式\06_例程_时钟之迹\02_工程例程\5-STM32时钟系统"

def step1_import_packs():
    """把 .pack（本质是 zip）解到 Keil 的 PACK 目录，免开 PackInstaller"""
    # Keil 用户级 pack 根目录（MDK5 默认装到 %LOCALAPPDATA%\Arm\Packs）
    pack_root = os.path.join(os.environ["LOCALAPPDATA"], "Arm", "PACK")
    jobs = [
        ("Keil.STM32F4xx_DFP.2.16.0.pack", os.path.join(pack_root, "Keil", "STM32F4xx_DFP", "2.16.0")),
        ("ARM.CMSIS.5.9.0.pack", os.path.join(pack_root, "ARM", "CMSIS", "5.9.0")),
    ]
    for fn, dest in jobs:
        src = os.path.join(PACKS, fn)
        if os.path.exists(dest) and os.path.exists(os.path.join(dest, ".ok")):
            print("[skip]", fn); continue
        os.makedirs(dest, exist_ok=True)
        with zipfile.ZipFile(src) as z:
            z.extractall(dest)
        open(os.path.join(dest, ".ok"), "w").write("ok")
        print("[installed]", fn, "->", dest)
    # 同时复制一份到 Keil 安装目录的 ARM\PACK（兼容部分工程写死路径）
    local_pack = os.path.join(KEIL, "ARM", "PACK")
    if os.path.isdir(local_pack):
        for fn, _ in jobs:
            shutil.copy2(os.path.join(PACKS, fn), local_pack)
        print("[copied] packs ->", local_pack)

def step2_build():
    if not os.path.exists(UV4):
        sys.exit("UV4.exe 不存在: " + UV4)
    uvprojx = glob.glob(os.path.join(PROJ, "**", "*.uvprojx"), recursive=True)
    if not uvprojx:
        sys.exit("找不到 uvprojx: " + PROJ)
    p = uvprojx[0]
    log = os.path.join(PACKS, "build_log.txt")
    print("[build]", p)
    r = subprocess.run([UV4, "-b", p, "-j0", "-o", log], capture_output=True, text=True, timeout=600)
    print("exit:", r.returncode, "(0/1=成功, 其他见 log)")
    if os.path.exists(log):
        txt = open(log, encoding="gbk", errors="ignore").read()
        tail = txt[-1500:]
        print(tail)
        ok = ("0 Error" in txt) or ("0 Error(s)" in txt)
        print("BUILD OK" if ok else "BUILD HAS ERRORS")

if __name__ == "__main__":
    step1_import_packs()
    step2_build()
