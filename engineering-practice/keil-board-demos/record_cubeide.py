import ctypes
import time
from pywinauto import Desktop
import pyautogui as p
from recorder import Recorder, BASE

D = Desktop(backend='win32')
w = D.window(handle=462084)
w.set_focus()
p.press('f8')
time.sleep(.6)
p.hotkey('ctrl', 'f2')
time.sleep(1)
r = Recorder('04_cubeide')
try:
    r.caption('STM32CubeIDE：同一份 GitHub 源码，也可使用电脑自带 GCC 编译\n按 Ctrl+B 构建 Pandora_Lab1 工程')
    p.hotkey('ctrl', 'b')
    time.sleep(5)
    p.screenshot().save(BASE / 'cube_record_build.png')
    r.caption('控制台显示：构建完成，0 错误、0 警告\n接着打开 运行 → 调试配置，连接板载 CMSIS-DAP')
    w.menu_select('运行(&R)->调试配置(&B)...')
    time.sleep(2)
    dialog = D.window(handle=ctypes.windll.user32.GetForegroundWindow())
    assert dialog.window_text() == '调试 配置'
    p.click(920, 292)
    time.sleep(.5)
    r.caption('调试器使用 CubeIDE 自带 OpenOCD；GDB 连接 127.0.0.1:3333\n先运行工程 tools/start_cubeide_debug.ps1，再启动此调试配置')
    time.sleep(5)
    p.click(1014, 292)
    time.sleep(.6)
    r.caption('此次附加到已烧录的 Keil 程序，符号文件使用匹配的 lab1_keil.axf\n关闭复位与 Load image，仅加载符号，不改写 Flash')
    time.sleep(5)
    buttons = [c for c in dialog.descendants() if c.friendly_class_name() == 'Button' and c.window_text() == '调试(&D)']
    assert len(buttons) == 1
    buttons[0].click_input()
    time.sleep(5)
    fg = D.window(handle=ctypes.windll.user32.GetForegroundWindow())
    if fg.window_text() == '确认切换透视图':
        for b in fg.descendants():
            if b.friendly_class_name() == 'Button' and b.window_text() == '切换(&S)':
                b.click_input()
                break
        time.sleep(2)
    r.caption('已停在板上实际运行的 main.c，左侧显示线程和调用栈\n右侧表达式读取 milliseconds 与 lab.mode = LAB_COLOR')
    p.click(2140, 124)
    time.sleep(5)
    p.screenshot().save(BASE / 'cube_record_debug.png')
    r.caption('按 F6 单步；按 F8 继续运行\n结束调试后 OpenOCD 释放连接，开发板继续执行')
    p.press('f6')
    time.sleep(3)
    p.press('f8')
    time.sleep(2)
    p.hotkey('ctrl', 'f2')
    time.sleep(3)
finally:
    r.stop()
