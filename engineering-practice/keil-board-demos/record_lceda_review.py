"""Record the actual professional EDA app; no fabricated interface frames."""
import ctypes
ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
from pathlib import Path
import shutil
import subprocess
import time
import pyautogui as p
from pywinauto import Desktop
from recorder import Recorder

BASE=Path(__file__).resolve().parent
for w in Desktop(backend='win32').windows():
    if '嘉立创EDA(标准版) 6.5.51' in w.window_text():
        w.set_focus()
        break
p.press('esc')
p.click(475,1476)
time.sleep(1)
rec=Recorder('07_lceda_native')
try:
    rec.caption('嘉立创 EDA 标准版：已导入并保存四页原生工程，元件、连线与流程框均可编辑。')
    time.sleep(6)
    p.click(1740,800)
    rec.caption('第1页：最小系统。U3 的全部100脚按 ST 数据核对；R13=10Ω，原厂旁注冲突已注明。')
    time.sleep(7)
    p.press('esc');p.click(642,1476)
    rec.caption('第2页：RGB、KEY0/KEY1、外部晶体与板载 DAP。USART1 的 J1 配对为1–4、2–3。')
    time.sleep(8)
    p.click(824,1476)
    rec.caption('第3页按 main.c 绘制：中断只记录边沿，主循环完成消抖、状态切换和低有效 LED 输出。')
    time.sleep(8)
    p.click(1005,1476)
    rec.caption('第4页：20ms消抖、停止键稳定按住时优先；14帧每帧300ms，COLOR灭帧与OFF状态不同。')
    time.sleep(8)
    rec.caption('嘉立创实际导出网表已核对25个网络、39个器件值；实物PCB版本和BOOT帽位未冒充已验证。')
    time.sleep(6)
finally:
    rec.stop()
subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','warning','-y',
                '-i','07_lceda_native_raw.mp4','-vf','ass=07_lceda_native.ass',
                '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
                '-movflags','+faststart','嘉立创EDA图纸检查演示.mp4'],cwd=BASE,check=True)
print('EDA walkthrough saved',flush=True)
