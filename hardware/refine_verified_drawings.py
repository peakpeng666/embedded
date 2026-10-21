#!/usr/bin/env python3
"""Refine the user's saved Verified drawings without rebuilding their layout."""
import argparse
import copy
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--input',type=Path,default=ROOT/'logs/Verified_用户修改快照.json')
ap.add_argument('--output',type=Path,default=ROOT/'logs/Verified_整理待应用.json')
args=ap.parse_args()
project=json.loads(args.input.read_text(encoding='utf-8-sig'))
before=copy.deepcopy(project)
updates={
 'ggePandora2':'正点原子 潘多拉 STM32L496VET6',
 'ggePandora76':'输入 5 V，输出 3.3 V；EN 与 VIN 相连。',
 'ggePandora454':'正点原子 潘多拉 STM32L496VET6',
 'ggePandora596':'共阳端接 VCC_3V3；R/G/B 经 1 kΩ 电阻连接 PE7/PE8/PE9。',
 'ggePandora648':'调试与串口接口',
 'ggePandora682':'J2：板载 DAP 控制器调试接口。',
 'ggePandora683':'板载 DAP / USB-UART 详细电路见原厂原理图第 2 页。',
 'ggePandora686':'实验接口与应用分区',
 'ggePandora687':'USB_COM：板载 DAP 与 USB-UART 复合接口。',
 'ggePandora688':'SWD：PA13 / SWDIO、PA14 / SWCLK、NRST。',
 'ggePandora689':'串口：COM3，115200 / 8N1 / 无流控。',
 'ggePandora690':'引导区：0x08000000–0x0800FFFF（64 KiB）。',
 'ggePandora691':'应用区：0x08010000–0x0807FFFF（448 KiB）。',
 'ggePandora692':'状态查询：发送 status；操作帮助：发送 help。',
 'ggePandora693':'KEY0 启动轮闪；KEY1 经主循环消抖后停止。',
 'ggePandora694':'RGB1 为共阳连接，PE7/8/9 输出低电平点亮。',
 'ggePandora697':'GPIO 与固件配置',
 'ggePandora703':'串口查询回传状态，运行模式由 KEY0 / KEY1 控制。',
 'ggePandora705':'正点原子 潘多拉 STM32L496VET6',
 'ggePandora706':'程序流程图：主循环与中断',
 'ggePandora738':'status / help：查询模式、计数与操作说明',
 'ggePandora765':'主循环连续处理按键、LED 和串口；LED 按 300 ms 帧周期更新。',
 'ggePandora789':'ISR 记录边沿与时间，主循环执行消抖、模式切换和 LED 更新。',
 'ggePandora811':'正点原子 潘多拉 STM32L496VET6',
 'ggePandora812':'程序流程图：按键消抖与 RGB 状态机',
 'ggePandora865':'EXTI 边沿到达：建立 KEY1 pending 请求',
 'ggePandora935':'KEY1 松开：更新按键稳定状态。',
 'ggePandora936':'KEY1 稳定按住：保持 OFF，等待松开。',
 'ggePandora937':'松开 KEY1 后再次按 KEY0，从红色重新开始。',
 'ggePandora938':'COLOR 包含 300 ms 灭帧；OFF 为停止状态。',
}
remove={'ggePandora31','ggePandora461','ggePandora712','ggePandora818'}
changes=[]
for i,sheet in enumerate(project['schematics'],1):
    shapes=[]
    for shape in sheet['dataStr']['shape']:
        parts=shape.split('~')
        if shape.startswith('T~L~'):
            key=parts[15]
            if key in remove:
                changes.append({'sheet':i,'id':key,'removed':parts[12]});continue
            if key in updates:
                changes.append({'sheet':i,'id':key,'before':parts[12],'after':updates[key]})
                parts[12]=updates[key]
            if key=='ggePandora3':parts[2:4]=['45','101']
            shape='~'.join(parts)
        if shape.startswith('R~') and '~ggePandora862~' in shape:
            parts[1:3]=['565','170'];shape='~'.join(parts)
        if shape.startswith('LIB~'):
            chunks=shape.split('#@$')
            refs=[c.split('~')[12] for c in chunks[1:] if c.startswith('T~P~')]
            if refs and refs[0] in {'R39','R41','R47'}:
                baseline=str(int(float(chunks[0].split('~')[2]))-13)
                for n,c in enumerate(chunks[1:],1):
                    if c.startswith(('T~P~','T~N~')):
                        f=c.split('~');f[2]='1265' if f[1]=='P' else '1315';f[3]=baseline
                        chunks[n]='~'.join(f)
                shape='#@$'.join(chunks)
        shapes.append(shape)
    if i==4 and not any(s.startswith('T~L~') and s.split('~')[12]=='4 / 4' for s in shapes):
        shapes.append('T~L~1645~1144~0~#16394D~Microsoft YaHei~11pt~~~~comment~4 / 4~1~end~ggeVerifiedPage4~0~')
    sheet['dataStr']['shape']=shapes
project['title']='Pandora_L496_Verified'
project['description']='潘多拉实验：最小系统、电路、主循环与中断、按键消抖与RGB状态机。'
# The only changed non-text graphic is the fourth-sheet title bar alignment.
def electrical(p):
    result=[]
    for sheet in p['schematics']:
        result.append([s for s in sheet['dataStr']['shape'] if s.startswith(('LIB~','W~','N~','J~','F~','O~'))])
    return result
def without_symbol_text(p):
    result=electrical(p)
    return [[('#@$'.join(c for c in s.split('#@$') if not c.startswith('T~')) if s.startswith('LIB~') else s) for s in sheet] for sheet in result]
assert without_symbol_text(before)==without_symbol_text(project)
assert len(project['schematics'])==4
args.output.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'logs/Verified_措辞调整记录.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Updated {len(changes)} annotations; electrical objects unchanged; {args.output}')
