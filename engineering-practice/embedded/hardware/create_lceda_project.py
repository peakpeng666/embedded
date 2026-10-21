#!/usr/bin/env python3
"""Editable EasyEDA Std schematics, drawn from vendor V3.4 and current code.

Uses the documented, open native file format. No imported bitmap or SVG circuit.
All pins, symbols, wires, labels and flowchart objects remain editable in LCEDA.
This is a partial analysis of an existing board, not fabrication-ready PCB data.
"""
import hashlib
import json
import math
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/lceda'
OUT.mkdir(parents=True, exist_ok=True)
PIN_SOURCE = ROOT / 'hardware/sources/STM32L496VETx_ST_CubeMX_pins.xml'
NS = {'m': 'http://mcd.rou.st.com/modules.php?name=mcu'}
PINS = {int(p.attrib['Position']): p.attrib['Name']
        for p in ET.parse(PIN_SOURCE).findall('m:Pin', NS)}
assert len(PINS) == 100 and set(PINS) == set(range(1, 101))

NAVY, INK, LINE, WIRE, PIN = '#16394D', '#263A49', '#B5C6D0', '#008000', '#880000'
BLUE, TEAL, PALE = '#000080', '#087F8C', '#F0F5F7'
SERIAL = 0
def gid():
    global SERIAL
    SERIAL += 1
    return f'ggePandora{SERIAL}'

def text(x, y, value, size=10, color=INK, kind='L', anchor='start', bold=False):
    assert not any(s in value for s in ['~', '#@$', '^^'])
    return f'T~{kind}~{x}~{y}~0~{color}~Microsoft YaHei~{size}pt~{("bold" if bold else "")}~~~comment~{value}~1~{anchor}~{gid()}~0~'

def poly(points, color=PIN, width=1, fill='none', closed=False):
    pts = ' '.join(str(v) for point in points for v in point)
    return f'{"PG" if closed else "PL"}~{pts}~{color}~{width}~0~{fill}~{gid()}~0'

def rect(x, y, w, h, color=PIN, fill='none', width=1):
    return f'R~{x}~{y}~~~{w}~{h}~{color}~{width}~0~{fill}~{gid()}~0~'

def ellipse(x, y, rx, ry, color=PIN, fill='none'):
    return f'E~{x}~{y}~{rx}~{ry}~{color}~1~0~{fill}~{gid()}~0'

def pin(num, name, x, y, direction='L', length=20, showname=True, shownum=True):
    # Coordinates are the outer connection point; body is in the given direction.
    dx, dy, rotation, anchor = {'L': (length, 0, 180, 'start'),
                               'R': (-length, 0, 0, 'end'),
                               'U': (0, length, 90, 'start'),
                               'D': (0, -length, 270, 'end')}[direction]
    ex, ey = x + dx, y + dy
    nx, ny = ex + (4 if dx > 0 else -4 if dx < 0 else 7), ey + 3
    tx, ty = (x+dx/2, y-4) if dx else (x-4, y+dy/2)
    return (f'P~show~0~{num}~{x}~{y}~{rotation}~{gid()}~0'
            f'^^{x}~{y}^^M {x} {y} L {ex} {ey}~{PIN}'
            f'^^{int(showname)}~{nx}~{ny}~0~{name}~{anchor}~Arial~8pt~{BLUE}'
            f'^^{int(shownum)}~{tx}~{ty}~0~{num}~middle~Arial~7pt~{BLUE}'
            f'^^0~{ex}~{ey}^^0~M {ex} {ey} L {ex} {ey}')

class Sheet:
    def __init__(self, title, index, subtitle):
        self.title, self.index, self.shapes, self.components = title, index, [], []
        self.add(rect(20,20,1650,1150,NAVY,width=1.3))
        self.t(45,66,'正点原子 潘多拉 / STM32L496VET6',22,NAVY,bold=True)
        self.t(45,101,title,16,TEAL,bold=True)
        self.t(45,132,subtitle,10)
        self.add(poly([(20,150),(1670,150)],LINE))
        self.add(poly([(20,1060),(1670,1060)],LINE))
        self.t(40,1087,'依据：潘多拉官方 V3.4 原理图 + 开发指南 V1.1；L496 引脚按 ST CubeMX / DS11585 核对。',10)
        self.t(40,1113,'范围：现有板的实验相关电路摘绘；省略网络不表示实板悬空。未配置 PCB 封装，不用于直接投板。',10)
        self.t(40,1144,'嘉立创 EDA 标准版 6.5.51 / 原生可编辑对象 / 2026-10-21',10,TEAL)
        self.t(1645,1144,f'{index} / 4',11,NAVY,anchor='end')
    def add(self,*items): self.shapes.extend(items)
    def t(self,x,y,value,size=10,color=INK,**kw): self.add(text(x,y,value,size,color,**kw))
    def lines(self,x,y,lines,size=10,step=23,color=INK):
        for i,l in enumerate(lines): self.t(x,y+i*step,l,size,color)
    def panel(self,x,y,w,h,title):
        self.add(rect(x,y,w,h,LINE),rect(x,y,w,30,LINE,PALE))
        self.t(x+12,y+21,title,11,NAVY,bold=True)
    def wire(self,*points): self.add('W~'+' '.join(str(v) for p in points for v in p)+f'~{WIRE}~1~0~none~{gid()}~0')
    def junction(self,x,y): self.add(f'J~{x}~{y}~2.5~{WIRE}~{gid()}~0')
    def net(self,x,y,name,anchor='start',dy=-5):
        self.add(f'N~{x}~{y}~0~#0000FF~{name}~{gid()}~{anchor}~{x}~{y+dy}~Arial~8pt~0')
    def port(self,p,name,direction='L',length=35):
        x,y=p; end=(x-length,y) if direction=='L' else (x+length,y)
        self.wire(p,end);self.net(*end,name,'end' if direction=='L' else 'start')
    def component(self,ref,value,x,y,parts,pins,desc='',textpos=None,bom=True):
        tx,ty = textpos or (x+10,y-22)
        # No guessed package association; named functional ports are explicit below.
        meta = f'package`NONE`spicePre`{ref.rstrip("0123456789")}`Manufacturer Part`{value}`Description`{desc}`'
        parts=[text(tx,ty,ref,9,BLUE,'P'),text(tx,ty+14,value,9,BLUE,'N')]+parts
        self.add(f'LIB~{x}~{y}~{meta}~0~0~{gid()}~~{uuid.uuid4().hex}~0~~no~{("yes" if bom else "no")}~~~#@$'+'#@$'.join(parts))
        self.components.append({'ref':ref,'value':value,'pins':{str(k):list(v) for k,v in pins.items()},'description':desc})
        return pins
    def resistor(self,ref,value,x,y,vertical=False):
        if vertical:
            parts=[rect(x-5,y-15,10,30),pin('1','',x,y-30,'U',15,False,False),pin('2','',x,y+30,'D',15,False,False)]
            pins={'1':(x,y-30),'2':(x,y+30)};tp=(x+13,y-3)
        else:
            parts=[rect(x-15,y-5,30,10),pin('1','',x-30,y,'L',15,False,False),pin('2','',x+30,y,'R',15,False,False)]
            pins={'1':(x-30,y),'2':(x+30,y)};tp=(x-23,y-25)
        return self.component(ref,value,x,y,parts,pins,textpos=tp)
    def cap(self,ref,value,x,y,polar=False):
        parts=[poly([(x-12,y-4),(x+12,y-4)]),poly([(x-12,y+4),(x+12,y+4)]),
               pin('1','',x,y-25,'U',21,False,False),pin('2','',x,y+25,'D',21,False,False)]
        if polar: parts.append(text(x-21,y-5,'+',9,PIN))
        return self.component(ref,value,x,y,parts,{'1':(x,y-25),'2':(x,y+25)},textpos=(x+18,y-5))
    def switch(self,ref,x,y):
        parts=[ellipse(x,y-18,2,2),ellipse(x,y+18,2,2),poly([(x,y+18),(x-12,y-12)]),
               pin('A','',x,y-30,'U',12,False,False),pin('B','',x,y+30,'D',12,False,False)]
        return self.component(ref,'按下接通',x,y,parts,{'A':(x,y-30),'B':(x,y+30)},
                              '功能端子 A/B；官方图未给物理焊盘脚序',textpos=(x+18,y-4))
    def bus_caps(self,refs,values,xs,y,topnet,botnet='GND',polar_last=False):
        for i,(ref,val,x) in enumerate(zip(refs,values,xs)):
            c=self.cap(ref,val,x,y,polar_last and i==len(refs)-1)
            self.wire(c['1'],(x,y-45));self.wire(c['2'],(x,y+45))
        self.wire((xs[0],y-45),(xs[-1],y-45));self.net(xs[0],y-45,topnet)
        self.wire((xs[0],y+45),(xs[-1],y+45));self.net(xs[0],y+45,botnet,dy=17)
        for x in xs[1:-1]: self.junction(x,y-45);self.junction(x,y+45)
    def arrow(self,points,color=TEAL,label=None):
        self.add(poly(points,color,1.4))
        (x0,y0),(x1,y1)=points[-2:];angle=math.atan2(y1-y0,x1-x0)
        a=[(x1,y1)]+[(round(x1-8*math.cos(angle+s),2),round(y1-8*math.sin(angle+s),2)) for s in (-.45,.45)]
        self.add(poly(a,color,1,color,True))
        if label:
            self.t((x0+x1)/2+5,(y0+y1)/2-6,label,9,color)
    def box(self,x,y,w,h,lines,diamond=False,fill=PALE,size=11):
        if diamond:
            self.add(poly([(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)],NAVY,1,fill,True))
        else: self.add(rect(x,y,w,h,NAVY,fill))
        if isinstance(lines,str): lines=[lines]
        start=y+h/2-(len(lines)-1)*9+4
        for i,l in enumerate(lines):self.t(x+w/2,start+i*18,l,size,INK,anchor='middle')
    def data(self):
        return {'docType':'1','title':self.title,'description':'按官方图与当前实现核对；详细依据见 hardware/README.md',
                'dataStr':{'head':{'docType':'1','editorVersion':'6.5.51','newgId':True,'c_para':{'Prefix Start':'1'},'hasIdFlag':True,'x':'0','y':'0','c_spiceCmd':None},
                           'canvas':'CA~1690~1190~#FFFFFF~yes~#CCCCCC~5~1690~1190~line~5~pixel~5~0~0',
                           'shape':self.shapes,'BBox':{'x':20,'y':20,'width':1650,'height':1150},'colors':{}}}

def sheet_minimum():
    s=Sheet('01 / 最小系统原理图：主控、电源、复位和启动',1,'按官方 V3.4 摘绘；U3 型号依官方开发指南更正为 L496；并非完整潘多拉生产图。')
    s.panel(40,170,900,245,'3.3 V 稳压 / U4 RT9013-3.3')
    parts=[rect(270,235,165,110),pin(1,'VIN',250,260),pin(2,'GND',250,285),pin(3,'EN',250,310),pin(5,'VOUT',455,260,'R'),pin(4,'NC',455,310,'R')]
    u=s.component('U4','RT9013-3.3',350,280,parts,{1:(250,260),2:(250,285),3:(250,310),5:(455,260),4:(455,310)},textpos=(290,213))
    s.wire(u[1],(175,260));s.net(175,260,'VCC_5V');s.wire(u[3],(205,310),(205,260));s.junction(205,260)
    s.port(u[2],'GND');s.port(u[5],'VCC_3V3','R',55)
    s.t(468,320,'NC（原图）',9)
    c=s.cap('C45','1uF',120,315);s.wire(c['1'],(120,260),(175,260));s.port(c['2'],'GND','L',25)
    s.bus_caps(['C42','C43','C44'],['1uF','100nF (104)','220uF/10V'],[575,695,825],315,'VCC_3V3',polar_last=True)
    s.t(65,393,'输入 5 V / 输出 3.3 V；EN 接输入；仅摘绘实验使用的主控供电支路。',10)
    s.panel(40,435,900,175,'数字电源与去耦 / 原图 R17、R18 并联，均为 0R')
    for ref,y in [('R17',505),('R18',560)]:
        r=s.resistor(ref,'0R',205,y);s.wire(r['1'],(140,y));s.wire(r['2'],(285,y))
    s.wire((140,505),(140,560));s.net(140,505,'VCC_3V3','end')
    s.wire((285,505),(285,560));s.net(285,505,'VCC_3.3M')
    s.bus_caps(['C37','C38','C39','C40','C41'],['100nF (104)']*5,[395,500,605,710,815],535,'VCC_3.3M')
    s.panel(40,630,900,185,'模拟电源与参考电压 / 保留官方实际器件标值')
    for ref,x,net,caprefs,values,xs in [('R15',205,'VDDA',['C30','C31'],['100nF (104)','10uF'],[315,430]),
                                      ('R13',580,'VREF+',['C28','C29'],['100nF (104)','2.2uF (225)'],[705,825])]:
        r=s.resistor(ref,'10R',x,700);s.port(r['1'],'VCC_3.3M' if ref=='R15' else 'VDDA',length=45)
        s.port(r['2'],net,'R',25);s.bus_caps(caprefs,values,xs,730,net)
    s.t(65,806,'原图 VREF 旁注写 R18，但对应器件明确标为 R13 / 10R；本图按器件标注，未实测阻值。',9,TEAL)
    s.panel(40,835,900,205,'复位 / BOOT0 选择（不假定实物跳线位置）')
    r=s.resistor('R16','10k',125,915,True);s.port(r['1'],'VCC_3V3','L',45)
    s.wire(r['2'],(125,965),(230,965));s.net(230,965,'RESET');s.junction(125,965)
    c=s.cap('C32','100nF (104)',125,1000);s.wire(c['1'],(125,965));s.port(c['2'],'GND','L',35)
    b=s.switch('RST1',300,995);s.wire(b['A'],(230,965));s.port(b['B'],'GND','R',35)
    parts=[rect(560,885,90,105)]+[pin(n,str(n),540,900+(n-1)*35,'L') for n in [1,2,3]]
    b=s.component('BOOT1','1x3 选择',605,935,parts,{n:(540,900+(n-1)*35) for n in [1,2,3]},textpos=(665,892))
    s.port(b[1],'VCC_3V3',length=40);s.port(b[3],'GND',length=40)
    r=s.resistor('R14','10k',440,935);s.wire(r['2'],b[2]);s.port(r['1'],'BOOT0',length=45)
    s.lines(685,940,['BOOT1：1 = 3.3 V，3 = GND','2 经 R14 接 BOOT0','本次不改选项字节；','未测得实物短接帽位置。'],9,22)
    # Exact 100-pin symbol from ST data, with every physical pin represented once.
    s.panel(975,170,675,870,'U3 / STM32L496VET6 / LQFP100 / 512 KiB Flash')
    power={11:'VCC_3.3M',28:'VCC_3.3M',50:'VCC_3.3M',75:'VCC_3.3M',100:'VCC_3.3M',6:'VCC_3.3M',73:'VCC_3.3M',
           10:'GND',27:'GND',49:'GND',74:'GND',99:'GND',19:'GND',20:'GND',22:'VDDA',21:'VREF+',14:'RESET',94:'BOOT0',
           8:'OSC32_IN',9:'OSC32_OUT',12:'OSC_IN',13:'OSC_OUT'}
    io={38:'LED_R',39:'LED_G',40:'LED_B',57:'KEY0',56:'KEY1',68:'UART1_TX',69:'UART1_RX',72:'T_JTMS',76:'T_JTCK'}
    left=list(power);right=list(io)
    remaining=[n for n in range(1,101) if n not in left+right]
    left+=remaining[:50-len(left)];right+=remaining[50-len(power):]
    assert len(left)==len(right)==50 and len(set(left+right))==100
    body=(1100,257,320,714)
    parts=[rect(*body)];positions={}
    for side,nums,x in [('L',left,1080),('R',right,1440)]:
        for i,n in enumerate(nums):
            y=270+i*14;parts.append(pin(n,PINS[n],x,y,side));positions[n]=(x,y)
    s.component('U3','STM32L496VET6',1260,610,parts,positions,'完整 100 引脚；脚号来自 ST CubeMX LQFP100 XML；未展开其余外围网络',textpos=(1110,222))
    for n,net in power.items():s.port(positions[n],net,'L',30)
    for n,net in io.items():s.port(positions[n],net,'R',35)
    s.lines(1000,1000,['原厂 V3.4 图中 U3 仍写 STM32L475VET6；型号依官方指南修正。','未展开的引脚保留原生端点，不加“实板未连接”标志。'],9,22)
    return s

def sheet_circuits():
    s=Sheet('02 / 实验电路图：RGB、按键、时钟与连板接口',2,'共阳 RGB 与按键低有效；当前固件用 HSI16，图上外部晶体仅是实板保留电路。')
    s.panel(40,170,780,260,'外部晶体 / 当前程序不依赖 HSE、LSE')
    # Original Y3 is a 4-pad passive crystal; grounded case pins are not omitted.
    for ref,x,value,caps,capvals,nets in [('Y2',235,'32.768kHz',['C33','C34'],['6pF','6pF'],['OSC32_IN','OSC32_OUT']),
                                          ('Y3',610,'8MHz',['C35','C36'],['22pF','22pF'],['OSC_IN','OSC_OUT'])]:
        parts=[rect(x-13,265,26,50),poly([(x-20,265),(x-20,315)]),poly([(x+20,265),(x+20,315)])]
        n_in,n_out=('1','3') if ref=='Y3' else ('IN','OUT')
        pp={n_in:(x-40,290),n_out:(x+40,290)}
        parts+=[pin(n_in,'',x-40,290,'L',20,False,ref=='Y3'),pin(n_out,'',x+40,290,'R',20,False,ref=='Y3')]
        if ref=='Y3':
            pp.update({'2':(x-8,345),'4':(x+8,345)})
            parts+=[pin('2','GND',x-8,345,'D',30,False,True),pin('4','GND',x+8,345,'D',30,False,True)]
        s.component(ref,value,x,290,parts,pp,'无源晶体；Y2 使用功能端子，原图未注明物理封装序号' if ref=='Y2' else '四焊盘无源晶体，2/4 接地',textpos=(x-28,239))
        for n,cname,val,xx,net in [(n_in,caps[0],capvals[0],x-85,nets[0]),(n_out,caps[1],capvals[1],x+85,nets[1])]:
            c=s.cap(cname,val,xx,350);s.wire(pp[n],(xx,290),c['1']);s.net(xx,290,net);s.port(c['2'],'GND','L' if xx<x else 'R',25)
        if ref=='Y3':
            s.wire(pp['2'],(x-8,390),(x+8,390),pp['4']);s.net(x,390,'GND',dy=17)
    s.t(60,416,'ST 脚号：PC14/8、PC15/9、PH0/12、PH1/13；当前 HSI16 = 16 MHz。',10)
    s.panel(850,170,800,260,'RGB1 / 共阳 RGB / PE7、PE8、PE9 低电平点亮')
    x,y=1055,300
    parts=[rect(x-65,y-55,130,115),pin('A','A',x-85,y,'L'),pin('R','R',x+85,y-35,'R'),pin('G','G',x+85,y,'R'),pin('B','B',x+85,y+35,'R')]
    # Functional ports only: vendor drawing does not specify RGB package numbering.
    for yy in [y-35,y,y+35]:
        parts += [poly([(x-30,yy-8),(x-30,yy+8),(x-14,yy)],PIN,1,'none',True),poly([(x-12,yy-9),(x-12,yy+9)]),poly([(x-12,yy),(x+65,yy)]),poly([(x-65,y),(x-45,y),(x-45,yy),(x-30,yy)])]
        for ox in [0,10]:
            parts += [poly([(x-14+ox,yy-11),(x-7+ox,yy-19)]),poly([(x-11+ox,yy-19),(x-7+ox,yy-19),(x-7+ox,yy-15)])]
    p=s.component('RGB1','共阳 / A-R-G-B 功能端',x,y,parts,{'A':(x-85,y),'R':(x+85,y-35),'G':(x+85,y),'B':(x+85,y+35)},'功能端名不代表物理焊盘序号；不指定封装',textpos=(980,221))
    s.port(p['A'],'VCC_3V3','L',70)
    for i,(ref,name) in enumerate([('R39','LED_R'),('R41','LED_G'),('R47','LED_B')]):
        yy=265+i*35;r=s.resistor(ref,'1k',1295,yy);s.wire(p['RGB'[i]],r['1']);s.port(r['2'],name,'R',90)
    s.lines(875,385,['PE7 / 38 → 红；PE8 / 39 → 绿；PE9 / 40 → 蓝。','RGB1 仅标功能端；官方图未给 RGB 封装脚序，不凭空编号。'],10,22)
    s.panel(40,450,780,270,'KEY0 / 查询启动；KEY1 / EXTI9 停止')
    for key,ref,x,net in [('KEY0','R45',210,'KEY0'),('KEY1','R42',590,'KEY1')]:
        r=s.resistor(ref,'10k',x,530,True);s.port(r['1'],'VCC_3V3','L',45)
        s.wire(r['2'],(x,585));s.net(x,585,net);s.junction(x,585)
        b=s.switch(key,x,625);s.wire((x,585),b['A']);s.port(b['B'],'GND','L',45)
    s.lines(65,684,['KEY0 = PD10 / 57：每 5 ms 查询，20 ms 消抖。','KEY1 = PD9 / 56：上升/下降沿中断，主循环进行 20 ms 消抖。'],10,22)
    s.panel(850,450,800,335,'实际连板路径 / 目标 SWD 与 USART1')
    s.add(rect(880,510,255,195,NAVY,PALE))
    s.lines(1007,538,[],10)
    s.t(1007,540,'板载 DAP / USB-UART',12,NAVY,anchor='middle',bold=True)
    s.t(1007,563,'USB_COM → PC',10,anchor='middle')
    # This module is a graphic functional boundary, not a fabricated physical IC.
    for yy,net in [(590,'T_JTMS'),(625,'T_JTCK'),(660,'RESET')]:
        s.wire((1135,yy),(1280,yy));s.net(1280,yy,net)
    s.t(1380,607,'PA13 / 72',10);s.t(1380,642,'PA14 / 76',10);s.t(1380,677,'NRST / 14',10)
    # Four exact physical J1 numbers; two demonstrated shunt paths.
    ps=[rect(1400,505,115,60),pin('1','',1380,520,'L',20,False),pin('2','',1380,550,'L',20,False),pin('4','',1535,520,'R',20,False),pin('3','',1535,550,'R',20,False)]
    j=s.component('J1','USART1 跳线',1455,535,ps,{'1':(1380,520),'2':(1380,550),'4':(1535,520),'3':(1535,550)},'短接配对 1-4、2-3；与 COM3 双向收发结果一致',textpos=(1410,476))
    s.port(j['1'],'DAP_RX','L',65);s.port(j['2'],'DAP_TX','L',65)
    s.port(j['4'],'UART1_TX','R',30);s.port(j['3'],'UART1_RX','R',30)
    s.wire(j['1'],j['4']);s.wire(j['2'],j['3'])
    s.wire((1135,520),(1315,520));s.wire((1135,550),(1315,550))
    s.t(1408,588,'短接：1–4、2–3',10,TEAL)
    s.lines(875,736,['J2 是 DAP 控制器自身调试接口，不当作目标 L496 的 SWD 接口。','DAP 功能框省略内部 U5 和 USB 保护电路；完整电路见厂商 PDF 第 2 页。'],10,23)
    s.panel(40,740,780,300,'证据与边界 / 不用软件读数替代未做的实物核验')
    s.lines(60,793,['已验证：CMSIS-DAP 识别、512 KiB Flash、Keil 下载和校验；','COM3 / 115200 / 8N1 / 无流控，STATUS / help 实际应答。','应用起始地址 0x08010000；保留前 64 KiB 引导程序。','未声称本轮实际按下实体按键；代码消抖和优先级有主机测试。','未确认：PCB 丝印版本、BOOT 短接帽位置、实际阻容测量值。','V3.4 与 DAP、Type-C 和使用的网络吻合，但不是实物版本读数。','板上其余传感器、无线和显示电路不在本次摘绘范围。','未展开的 GPIO 保留在第 1 页 U3 上，不标为实板未连接。'],10,27)
    s.panel(850,805,800,235,'代码、电路和运行状态的一致性')
    s.lines(875,857,['GPIO：PE7/8/9 推挽，预置高电平再切换输出，防止启动闪亮。','按键：PD10 / PD9 输入上拉；KEY0 不配置 EXTI，KEY1 双沿触发。','串口：PA9 TX / PA10 RX，AF7；HSI16 / BRR139 ≈ 115200 baud。','RGB：R、灭、G、灭、B、灭、Y、灭、C、灭、M、灭、W、灭。','每帧 300 ms，14 帧 = 4.2 s；彩灯间的灭帧仍属于 COLOR 状态。','图纸是静态原理图，不把 Proteus F401 示例宣称为 L496 仿真。'],10,27)
    return s

def sheet_flow_main():
    s=Sheet('03 / 程序流程图：初始化、主循环与中断',3,'依据 lab1/src/main.c；所有方框、判断框与箭头均为可编辑 EDA 图元。')
    s.panel(40,170,780,870,'主程序 / thread mode')
    nodes=[(210,220,420,48,['复位入口 / main()'],False),
           (110,295,620,88,['hardware_init()：关中断、清中断状态、VTOR=0x08010000','切到 HSI16；GPIO、USART1、EXTI9、SysTick 初始化','lab_init() → OFF；使能中断'],False),
           (180,410,480,52,['打印启动状态；last_poll = milliseconds'],False),
           (150,490,360,70,['距离上次查询 ≥ 5 ms？'],True),
           (150,600,540,57,['原子复制 IRQ 邮箱并清 pending','有新边沿则调用 lab_key1_edge()'],False),
           (150,690,540,57,['重新采样 milliseconds；若 KEY1 pending','调用 lab_service_key1()，有效按下时打印状态'],False),
           (150,780,540,57,['lab_led_mask() 计算当前 RGB mask','仅 mask 改变时更新 GPIOE BSRR'],False),
           (150,870,540,57,['uart_service()：处理 RX，非阻塞排空 TX','status / help 查询不修改灯的模式'],False)]
    for x,y,w,h,ls,d in nodes:s.box(x,y,w,h,ls,d,size=10)
    for a,b in zip(nodes[:2],nodes[1:3]):
        s.arrow([(a[0]+a[2]/2,a[1]+a[3]),(b[0]+b[2]/2,b[1])])
    s.arrow([(420,462),(420,475),(330,475),(330,490)])
    s.box(560,490,235,70,['last_poll = now','lab_poll_key0()','有效按下则打印'],size=9)
    s.arrow([(510,525),(560,525)],label='是')
    s.arrow([(330,560),(330,580),(420,580),(420,600)])
    s.t(338,578,'否',9,TEAL)
    s.arrow([(677.5,560),(677.5,580),(420,580),(420,600)])
    for a,b in zip(nodes[4:],nodes[5:]):s.arrow([(420,a[1]+a[3]),(420,b[1])])
    s.arrow([(420,927),(420,970),(80,970),(80,475),(330,475),(330,490)])
    s.t(95,1007,'循环不调用 delay / WFI；300 ms 是状态机计时，不阻塞串口。',10,TEAL)
    s.panel(850,170,800,505,'EXTI9_5_IRQHandler / KEY1 边沿')
    s.box(1020,220,460,50,'进入 EXTI9_5_IRQHandler')
    s.box(1070,305,360,80,'PR1 的 line9 置位？',True)
    s.box(970,425,560,90,['写 PR1 清 line9；irq_time = milliseconds','irq_pressed = key1_down()；irq_count++','irq_pending = true'],size=11)
    s.box(1100,575,300,48,'异常返回')
    s.arrow([(1250,270),(1250,305)])
    s.arrow([(1250,385),(1250,425)],label='是')
    s.arrow([(1430,345),(1600,345),(1600,555),(1250,555),(1250,575)])
    s.t(1460,334,'否',9,TEAL)
    s.arrow([(1250,515),(1250,575)])
    s.t(878,651,'ISR 只记录边沿和时间；消抖、模式切换与 LED 更新均在主循环。',10,TEAL)
    s.panel(850,700,800,340,'SysTick_Handler / 1 ms 节拍与主循环的 LED 更新')
    s.box(920,760,290,50,'每 1 ms 进入 SysTick')
    s.box(920,850,290,50,'milliseconds++')
    s.box(920,940,290,50,'异常返回')
    s.arrow([(1065,810),(1065,850)]);s.arrow([(1065,900),(1065,940)])
    s.lines(1260,783,['LED 写入（低有效）：','on = (mask << 7) & LED_PINS','BSRR 低 16 位：未点亮脚置高','BSRR 高 16 位：点亮脚拉低','','EXTI 邮箱在关中断区间复制，','随后立即开中断，主循环处理。'],10,28)
    return s

def sheet_flow_logic():
    s=Sheet('04 / 程序流程图：按键消抖、停止优先与 RGB 状态机',4,'依据 lab_logic.c / lab_logic.h；查询周期 5 ms，消抖 20 ms，RGB 每帧 300 ms。')
    s.panel(40,170,500,870,'KEY0 / lab_poll_key0()')
    s.box(100,220,380,52,'每 5 ms 采样 PD10，低为按下')
    s.box(75,310,430,72,['采样与 candidate 不同则更新 candidate','since = now'],size=10)
    s.box(100,430,380,88,['采样 ≠ stable','且稳定 ≥ 20 ms？'],True)
    s.box(105,565,370,62,['更新 stable','按下沿才增加 key0_presses'],size=10)
    s.box(100,685,380,90,['按下，且 KEY1 未稳定按住？'],True,size=10)
    s.box(105,825,370,65,['mode = COLOR','frame = 0；frame_start = now'],size=10)
    s.box(170,955,240,44,'返回主循环',size=10)
    s.arrow([(290,272),(290,310)]);s.arrow([(290,382),(290,430)])
    s.arrow([(290,518),(290,565)],label='是');s.arrow([(290,627),(290,685)])
    s.arrow([(290,775),(290,825)],label='是');s.arrow([(290,890),(290,955)])
    s.arrow([(480,474),(520,474),(520,977),(410,977)])
    s.t(490,463,'否',9,TEAL)
    s.arrow([(100,730),(65,730),(65,977),(170,977)])
    s.t(70,717,'否',9,TEAL)
    s.panel(565,170,550,870,'KEY1 / lab_service_key1()')
    s.box(650,220,380,52,'仅真实 EXTI 边沿建立 pending')
    s.box(630,310,420,88,['当前采样 = candidate？'],True)
    s.box(650,440,380,65,['已稳定 ≥ 20 ms？'],True)
    s.box(625,555,430,70,['清 pending；若 stable 改变则更新','仅按下沿增加 key1_presses'],size=10)
    s.box(650,680,380,80,'是否有效按下沿？',True)
    s.box(650,815,380,64,['mode = OFF','frame = 0；frame_start = now'],size=10)
    s.box(725,955,230,44,'返回主循环',size=10)
    s.arrow([(840,272),(840,310)])
    s.arrow([(840,398),(840,440)],label='是');s.arrow([(840,505),(840,555)],label='是')
    s.arrow([(840,625),(840,680)]);s.arrow([(840,760),(840,815)],label='是');s.arrow([(840,879),(840,955)])
    s.arrow([(1050,354),(1090,354),(1090,977),(955,977)])
    s.t(1060,343,'否',9,TEAL)
    s.t(1075,405,'重置',9,TEAL,anchor='end');s.t(1075,425,'候选/时间',9,TEAL,anchor='end')
    s.arrow([(650,472),(590,472),(590,977),(725,977)])
    s.t(600,461,'否',9,TEAL)
    s.arrow([(1030,720),(1070,720),(1070,977),(955,977)])
    s.t(1040,709,'否',9,TEAL)
    s.panel(1140,170,510,870,'RGB / lab_led_mask()')
    s.box(1220,220,350,50,'主循环请求当前 mask')
    s.box(1220,315,350,80,'mode == OFF？',True)
    s.box(1205,455,380,105,['elapsed = (now - frame_start) / 300','frame = (frame + elapsed) % 14','frame_start += elapsed × 300','返回 blink[frame]'],size=10)
    s.box(1250,620,290,48,'返回主循环',size=10)
    s.arrow([(1395,270),(1395,315)])
    s.arrow([(1395,395),(1395,455)],label='否 / COLOR')
    s.arrow([(1570,355),(1625,355),(1625,644),(1540,644)])
    s.t(1600,423,'是：mask=0',9,TEAL,anchor='end')
    s.arrow([(1395,560),(1395,620)])
    s.lines(1165,725,['blink = [1,0,2,0,4,0,3,0,6,0,5,0,7,0]','R → 灭 → G → 灭 → B → 灭 → Y → 灭','→ C → 灭 → M → 灭 → W → 灭','14 帧 × 300 ms = 4.2 s','','KEY1 松开不自动启动。','KEY1 稳定按住期间 KEY0 不启动；','松开 KEY1 后需再次按 KEY0。','COLOR 的灭帧不等于 OFF 状态。'],10,29)
    return s

def main():
    sheets=[sheet_minimum(),sheet_circuits(),sheet_flow_main(),sheet_flow_logic()]
    project={'editorVersion':'6.5.51','docType':'5','title':'Pandora_L496_Official_Code_Review',
             'description':'正点原子潘多拉：官方电路与实际代码核对；原生可编辑四页图纸。',
             'colors':{},'schematics':[s.data() for s in sheets]}
    path=OUT/'Pandora_L496_schematic-and-flowcharts.json'
    path.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
    for i,s in enumerate(sheets,1):
        data=s.data()['dataStr']
        (OUT/f'{i:02d}_sheet.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest={'project':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
              'st_pin_source_sha256':hashlib.sha256(PIN_SOURCE.read_bytes()).hexdigest(),
              'mcu_pin_count':100,'sheets':[{'title':s.title,'shapes':len(s.shapes),'components':s.components} for s in sheets]}
    (OUT/'design_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'file':str(path),'bytes':path.stat().st_size,'sheet_objects':[len(s.shapes) for s in sheets],'mcu_pins':len(PINS)},ensure_ascii=False))

if __name__=='__main__':main()
