import time
import pyautogui as p
from pywinauto import Desktop
from recorder import Recorder, BASE

w = Desktop(backend='win32').window(handle=135668)
w.set_focus()
p.click(310, 194)
time.sleep(.5)
r = Recorder('05_cubemx')
try:
    r.caption('STM32CubeMX：打开 cubemx/Pandora_L496.ioc\n型号 STM32L496VETx、LQFP100，与当前开发板一致')
    time.sleep(6)
    r.caption('引脚：PE7 / PE8 / PE9 为 RGB；PD10 为 KEY0，PD9 为 KEY1 EXTI\nPA9 / PA10 为 USART1；PA13 / PA14 保留 SWD 调试')
    p.moveTo(1865, 1036, duration=.6)
    time.sleep(6)
    r.caption('Clock Configuration：查看系统时钟树\nHSI 内部时钟 16 MHz，SYSCLK、HCLK、APB1、APB2 均为 16 MHz')
    p.click(961, 194)
    time.sleep(7)
    r.caption('这份 .ioc 用于核对引脚与时钟配置\n现有裸机源码在 main.c 中完成对应的寄存器初始化')
    time.sleep(5)
    p.click(310, 194)
    time.sleep(.5)
    p.hotkey('ctrl', 's')
    time.sleep(3)
    p.screenshot().save(BASE / 'mx_record_final.png')
finally:
    r.stop()
