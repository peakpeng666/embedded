import ctypes
from pathlib import Path
import time
from pywinauto import Desktop
import pyautogui as pg
from recorder import Recorder

VIZ=Path(r"C:/Users/Peak/.codex/visualizations/2026/10/21/01a15c34-f234-7f71-bee6-8ce5e1048a3b")
d=Desktop(backend="win32")
m=d.window(handle=199596);m.set_focus()
u=ctypes.windll.user32;u.LoadKeyboardLayoutW.restype=ctypes.c_void_p
u.PostMessageW(m.handle,0x50,0,u.LoadKeyboardLayoutW("00000409",1))
r=Recorder("03_mobaxterm")
try:
    r.caption("MobaXterm：连接板载 USB_COM 串口\n点击 Session → Serial，端口选择 COM3，速率 115200")
    pg.click(40,88);time.sleep(.4)
    w=d.window(title="Session settings");w.set_focus()
    pg.click(1343,460);time.sleep(.3)
    edits=[c for c in w.descendants(class_name="Edit") if c.is_visible()]
    edits.sort(key=lambda c:c.rectangle().left)
    assert len(edits)==2
    edits[0].set_edit_text("COM3");edits[1].set_edit_text("115200")
    time.sleep(4)
    pg.click(797,740);time.sleep(.3)
    pg.click(1050,972);pg.press("home");pg.press("enter");time.sleep(.4)
    r.caption("Advanced Serial settings：8 数据位、1 停止位、无校验\nFlow control 选择 None；这些参数与固件的 115200 / 8N1 对应")
    pg.screenshot().save(VIZ/"recorded_moba_serial_parameters.png")
    time.sleep(5)
    ok=[c for c in w.descendants() if c.is_visible() and c.window_text()=="OK"][0]
    ok.click_input();time.sleep(1)
    pg.click(800,450)
    r.caption("连接后输入 status，再按 Enter\nmode=COLOR 表示程序正在轮闪；按键次数和丢包计数也会返回")
    pg.write("status",interval=.15);pg.press("enter");time.sleep(4)
    r.caption("输入 help，再按 Enter，查看固件提供的命令\nKEY0 启动轮闪，KEY1 停止；这些按键在开发板上操作")
    pg.write("help",interval=.15);pg.press("enter");time.sleep(5)
    pg.screenshot().save(VIZ/"recorded_moba_status_help.png")
    r.caption("串口用于查看日志、状态和命令交互\n修改代码并下载后，可以在这里检查新程序的运行结果")
    time.sleep(4)
finally:
    r.stop()
