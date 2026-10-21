from pathlib import Path
import hashlib
import json
import time

from pywinauto import Desktop
import pyautogui as pg

from recorder import Recorder, BASE

ROOT = BASE.parent / "embedded"
VIZ = Path(r"C:/Users/Peak/.codex/visualizations/2026/10/21/01a15c34-f234-7f71-bee6-8ce5e1048a3b")
validation = json.loads((ROOT / "keil/Objects/validation.json").read_text())
image = (ROOT / "keil/Objects/lab1_keil.bin").read_bytes()
assert len(image) <= 4096 and validation["flash_address"] == "0x08010000"
assert hashlib.sha256(image).hexdigest() == validation["sha256"]
before = json.loads((ROOT / "logs/windows_before_keil.json").read_text())
assert len(Path(before["file"]).read_bytes()) == 524288

desktop = Desktop(backend="win32")
keil = desktop.window(title_re=".*lab1.uvprojx.*Vision.*")
assert keil.is_enabled()
keil.set_focus()
pg.click(650, 400)
recording = Recorder("01_keil_download")
try:
    recording.caption("Keil µVision：打开 GitHub 工程，编译并下载到 STM32L496\n板载 CMSIS-DAP + USB_COM，Windows 已识别 COM3")
    pg.click(50, 232)
    time.sleep(5)
    recording.caption("应用源码位于 lab1/src；KEY0 查询启动 RGB，KEY1 外部中断停止\n打开目标选项：Alt+F7")
    pg.hotkey("alt", "f7")
    time.sleep(.6)
    options = desktop.window(title_re="Options for Target.*")
    options.set_focus()
    pg.click(934, 480)
    time.sleep(5)
    recording.caption("Target：STM32L496VETx；IROM1 起始地址 0x08010000\n应用从 64 KiB 之后开始，保留板上引导程序")
    time.sleep(5)
    pg.click(1444, 480)
    time.sleep(.4)
    options.child_window(control_id=1523, class_name="Button").click()
    time.sleep(.7)
    setup = desktop.window(title="CMSIS-DAP Cortex-M Target Driver Setup")
    assert setup.child_window(control_id=1002, class_name="Edit").window_text() == "ATK-03262021"
    recording.caption("Debug → CMSIS-DAP Debugger → Settings\n已识别 ATK-03262021，使用 SWD，时钟 100 kHz")
    pg.screenshot().save(VIZ / "recorded_keil_probe.png")
    time.sleep(6)
    pg.click(1045, 530)
    time.sleep(.5)
    assert setup.child_window(control_id=1201, class_name="Button").get_check_state() == 1
    assert setup.child_window(control_id=1203, class_name="Button").get_check_state() == 1
    assert setup.child_window(control_id=1204, class_name="Button").get_check_state() == 1
    algorithm = setup.child_window(control_id=1210, class_name="SysListView32").wrapper_object()
    assert algorithm.item_count() == 1
    assert "512 KB" in algorithm.get_item(0, 0).text()
    recording.caption("Flash Download：Erase Sectors、Program、Verify\n选择 STM32L4xx 512 KB Flash；当前镜像占用两个 2 KiB 页面")
    pg.screenshot().save(VIZ / "recorded_keil_flash_options.png")
    time.sleep(7)
    setup.child_window(control_id=1, class_name="Button").click()
    time.sleep(.3)
    options.child_window(control_id=1, class_name="Button").click()
    time.sleep(.3)
    keil.set_focus()
    recording.caption("编译：按 F7，检查 Build Output\n此工程使用电脑已有的 Arm Compiler 5.06")
    pg.press("f7")
    time.sleep(5)
    pg.screenshot().save(VIZ / "recorded_keil_build.png")
    recording.caption("下载：按 F8，将刚编译的 3344 字节程序写入应用区\n下载完成后检查 Verify OK，再进入调试运行")
    pg.press("f8")
    time.sleep(9)
    pg.screenshot().save(VIZ / "recorded_keil_download_result.png")
    if not keil.is_enabled():
        raise RuntimeError("Keil displayed a modal dialog after download; inspect screenshot")
    recording.caption("查看下载结果：Erasing / Programming / Verify\n下一步进入硬件调试，再通过串口查询运行状态")
    time.sleep(5)
finally:
    recording.stop()
