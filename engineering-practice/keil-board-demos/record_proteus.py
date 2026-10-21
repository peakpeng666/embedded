import time
import ctypes
from pywinauto import Desktop
import pyautogui as p
from recorder import Recorder, BASE

D = Desktop(backend='win32')
d = D.window(handle=463396)
d.child_window(handle=200908).click_input()
time.sleep(.3)
w = D.window(handle=135732)
w.set_focus()
r = Recorder('06_proteus')
try:
    r.caption('Proteus 8：打开电脑已有的 STM32F401 + HD44780 LCD 仿真工程\n用途是软件电路仿真；前面实际连接的开发板是 STM32L496')
    time.sleep(5)
    p.doubleClick(2070, 670, interval=.15)
    time.sleep(.5)
    r.caption('双击 U1 查看设置：STM32F401VE，Program File = main.elf\n修改对应源码、重新编译 ELF 后，可在此加载并重新仿真')
    time.sleep(6)
    d = D.window(handle=ctypes.windll.user32.GetForegroundWindow())
    for b in d.descendants():
        if b.friendly_class_name() == 'Button' and b.window_text() == '取消(&C)':
            b.click_input()
            break
    p.click(32, 1506)
    time.sleep(3)
    r.caption('点击左下角三角形开始仿真\nLCD 显示 Peak STM32 Lab，并持续更新 Count 计数')
    time.sleep(7)
    p.screenshot().save(BASE / 'proteus_record_running.png')
    r.caption('可使用暂停、单步与停止按钮观察程序\n完成后点击方形停止；实物开发继续使用 Keil / CubeIDE 与串口工具')
    p.click(139, 1506)
    time.sleep(3)
    p.click(194, 1506)
    time.sleep(3)
    p.screenshot().save(BASE / 'proteus_record_stopped.png')
finally:
    r.stop()
