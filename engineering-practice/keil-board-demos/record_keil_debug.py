from pathlib import Path
import time
from pywinauto import Desktop
import pyautogui as pg
from recorder import Recorder

VIZ=Path(r"C:/Users/Peak/.codex/visualizations/2026/10/21/01a15c34-f234-7f71-bee6-8ce5e1048a3b")
d=Desktop(backend="win32")
w=d.window(title_re=".*lab1.uvprojx.*Vision.*")
w.set_focus()
r=Recorder("02_keil_debug")
def command(text):
    c=w.child_window(control_id=107,class_name="Edit").wrapper_object()
    c.set_edit_text(text);c.set_focus();pg.press("enter");time.sleep(.4)
try:
    r.caption("Keil 硬件调试：Ctrl+F5 进入调试，F5 运行，F10 单步\n当前 Flash 已通过整片读回比对，应用镜像与 AXF 对应")
    pg.hotkey("ctrl","f5");time.sleep(6)
    assert w.is_enabled(), "Unexpected modal dialog entering Keil debugger"
    command('LOAD "Objects/lab1_keil.axf" NOCODE')
    r.caption("在 Command 输入 BS main，为 main 设置断点\nF5 运行，程序会停在黄色箭头标出的源代码位置")
    command("BS main");pg.press("f5");time.sleep(4)
    pg.screenshot().save(VIZ/"recorded_keil_main_breakpoint.png")
    r.caption("F10：执行当前语句并停到下一条；左侧寄存器同步变化\n可以观察硬件初始化、串口输出和主循环")
    pg.press("f10");time.sleep(2);pg.press("f10");time.sleep(3)
    r.caption("查看程序变量：milliseconds 是毫秒计数，lab.mode 是灯的模式\n在 Command 中使用 printf，或用 WS 添加到 Watch 窗口")
    command('printf("ticks=%u mode=%u\\n", milliseconds, lab.mode)')
    command("WS 1, milliseconds, 10");command("WS 1, lab.mode, 10")
    time.sleep(3)
    r.caption("调试演示：将 lab.mode 改成 1（COLOR），再按 F5 运行\n这是通过调试器修改 RAM 变量；板上的 KEY0/KEY1 仍可正常使用")
    command("lab.mode = 1")
    command("BK *")
    pg.press("f5");time.sleep(5)
    r.caption("结束调试前先让程序运行，再按 Ctrl+F5 退出\n接下来在 MobaXterm 的 COM3 中查询程序状态")
    pg.hotkey("ctrl","f5");time.sleep(4)
    pg.screenshot().save(VIZ/"recorded_keil_debug_finished.png")
finally:
    r.stop()
