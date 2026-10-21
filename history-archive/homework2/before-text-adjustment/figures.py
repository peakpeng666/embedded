from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

OUT=Path(__file__).resolve().parents[1]/'配图'
OUT.mkdir(exist_ok=True)
BLACK='#17252D'; TEAL='#236A73'; LIGHT='#EDF3F4'; GREY='#64747D'; LINE='#A8B7BC'
class Fig:
    def __init__(self,w,h):
        self.w=w;self.h=h;self.k=3
        self.im=Image.new('RGB',(w*3,h*3),'white');self.d=ImageDraw.Draw(self.im)
    def xy(self,p):return tuple(round(v*self.k) for v in p)
    def text(self,x,y,s,size=25,fill=BLACK,bold=False,mono=False,anchor='lt'):
        font='consola.ttf' if mono else ('msyhbd.ttc' if bold else 'msyh.ttc')
        f=ImageFont.truetype(str(Path('C:/Windows/Fonts')/font),int(size*self.k))
        if '\n' in s and anchor.endswith('t'):
            for i,line in enumerate(s.splitlines()):
                self.d.text(self.xy((x,y+i*(size+7))),line,font=f,fill=fill,anchor=anchor)
            return
        self.d.text(self.xy((x,y)),s,font=f,fill=fill,anchor=anchor,spacing=7*self.k)
    def line(self,p,fill=TEAL,width=2):self.d.line([self.xy(q) for q in p],fill=fill,width=round(width*self.k))
    def rect(self,box,fill=LIGHT,outline=LINE):self.d.rectangle(self.xy(box),fill=fill,outline=outline,width=2*self.k)
    def dot(self,x,y):self.d.ellipse(self.xy((x-4,y-4,x+4,y+4)),fill=TEAL)
    def arrow(self,p,fill=TEAL):
        self.line(p,fill,2)
        a,b=p[-2:]; ang=math.atan2(b[1]-a[1],b[0]-a[0]);l=13
        q1=(b[0]-l*math.cos(ang-.42),b[1]-l*math.sin(ang-.42))
        q2=(b[0]-l*math.cos(ang+.42),b[1]-l*math.sin(ang+.42))
        self.d.polygon([self.xy(b),self.xy(q1),self.xy(q2)],fill=fill)
    def box(self,x,y,w,h,title,sub=None):
        self.rect((x,y,x+w,y+h))
        self.text(x+w/2,y+(22 if sub else h/2),title,26,bold=True,anchor='mt' if sub else 'mm')
        if sub:self.text(x+w/2,y+65,sub,21,anchor='mt')
    def ground(self,x,y):
        self.line([(x,y),(x,y+12)])
        for k,sz in enumerate([16,10,4]):self.line([(x-sz,y+12+k*7),(x+sz,y+12+k*7)])
    def resistor(self,x,y,vertical=True,label=None):
        if vertical:
            self.line([(x,y),(x,y+15)]);self.rect((x-9,y+15,x+9,y+60),'white',TEAL);self.line([(x,y+60),(x,y+75)])
            if label:self.text(x+18,y+28,label,20)
        else:
            self.line([(x,y),(x+15,y)]);self.rect((x+15,y-9,x+60,y+9),'white',TEAL);self.line([(x+60,y),(x+75,y)])
            if label:self.text(x+35,y-35,label,20,anchor='mt')
    def cap(self,x,y,label):
        self.line([(x,y),(x,y+25)]);self.line([(x-18,y+25),(x+18,y+25)],width=3)
        self.line([(x-18,y+35),(x+18,y+35)],width=3);self.line([(x,y+35),(x,y+55)])
        self.text(x+25,y+18,label,20);self.ground(x,y+55)
    def save(self,name):
        self.im.save(OUT/(name+'.png'),dpi=(300,300));return OUT/(name+'.png')

f=Fig(1200,570)
rows=[('0xE0000000—0xFFFFFFFF','系统区','PPB / SCS / SysTick'),
      ('0xA0000000—0xDFFFFFFF','外部设备区','外部设备映射'),
      ('0x60000000—0x9FFFFFFF','外部 RAM 区','外部存储器映射'),
      ('0x40000000—0x5FFFFFFF','外设区','GPIO / TIM / USART / CAN'),
      ('0x20000000—0x3FFFFFFF','SRAM 区','片内 SRAM / 位带别名'),
      ('0x00000000—0x1FFFFFFF','代码区','Flash / 启动映射')]
for i,(addr,title,desc) in enumerate(rows):
    y=10+i*89;f.text(5,y+27,addr,26,mono=True)
    f.rect((510,y,1190,y+79),'#DCECED' if i in (0,3) else '#F2F4F4')
    f.text(533,y+13,title,26,bold=True);f.text(790,y+17,desc,21)
f.save('01_存储器映射')

f=Fig(1200,485)
for x,y,t,s in [(5,5,'中断源产生请求','按键边沿 / 定时器更新等'),(430,5,'NVIC 挂起与仲裁','使能位 / 屏蔽位 / 优先级'),
                (855,5,'响应异常','硬件压栈 / 读取向量'),(855,290,'执行 ISR','处理事件 / 清除外设标志'),
                (430,290,'异常返回','恢复上下文'),(5,290,'继续原程序','或处理其他挂起异常')]:
    f.box(x,y,335,145,t,s)
f.arrow([(340,77),(430,77)]);f.arrow([(765,77),(855,77)])
f.arrow([(1022,150),(1022,290)]);f.arrow([(855,360),(765,360)]);f.arrow([(430,360),(340,360)])
f.line([(600,150),(600,205),(465,205)],GREY)
f.arrow([(465,205),(465,150)],GREY);f.text(225,198,'未满足响应条件时保持挂起',19,GREY)
f.text(1040,199,'抢占',21,TEAL)
f.save('02_中断流程')

f=Fig(1200,630)
f.rect((5,10,420,510));f.text(28,26,'主端口 8 个',28,bold=True)
left=['CPU I-bus','CPU D-bus','CPU S-bus','DMA1 memory','DMA2 memory','DMA2 peripheral','Ethernet DMA','USB OTG HS DMA']
for i,t in enumerate(left):f.text(32,90+i*49,t,25,mono=True)
f.rect((520,180,655,345),'#DCECED');f.text(588,262,'AHB\n矩阵',25,bold=True,anchor='mm')
f.arrow([(420,260),(520,260)]);f.arrow([(655,260),(758,260)])
f.rect((758,10,1195,510));f.text(782,26,'从端口 7 个',28,bold=True)
right=['Flash ICode 接口','Flash DCode 接口','SRAM1  112 KB','SRAM2  16 KB','AHB1 及 APB1 / APB2','AHB2 外设','FSMC 外部存储器接口']
for i,t in enumerate(right):f.text(784,95+i*55,t,23)
f.text(7,548,'CCM 64 KB：CPU D-bus 专用访问；DMA1 外设端口直接连接 APB1。',25)
f.save('03_总线结构')

f=Fig(1200,400)
f.box(5,70,240,130,'HSE 8 MHz','外部晶振')
f.box(328,70,300,130,'PLL 168 MHz','÷ 8 × 336 ÷ 2')
f.box(710,70,235,130,'HCLK 168 MHz','AHB ÷ 1')
f.arrow([(245,135),(328,135)]);f.arrow([(628,135),(710,135)])
f.line([(945,135),(975,135),(975,20)]);f.arrow([(975,20),(1195,20)])
f.text(982,44,'APB2 ÷ 2',22);f.text(982,90,'84 MHz',28,bold=True)
f.line([(975,135),(975,228)]);f.arrow([(975,228),(1195,228)])
f.text(982,248,'APB1 ÷ 4',22);f.text(982,294,'42 MHz',28,bold=True)
f.line([(478,200),(478,282)]);f.arrow([(478,282),(715,282)])
f.text(250,310,'PLLQ = 7：336 MHz ÷ 7 → 48 MHz',25)
f.save('04_时钟树')

f=Fig(1200,360)
f.text(280,4,'3.3 V',25,anchor='mt');f.line([(280,36),(280,50)])
f.resistor(280,50,label='10 kΩ');f.line([(280,125),(280,170),(725,170)])
f.dot(280,170);f.cap(280,170,'100 nF')
f.dot(510,170);f.line([(510,170),(510,213)])
f.line([(492,216),(535,195)],width=3);f.line([(510,239),(510,260)])
f.ground(510,260);f.text(540,226,'复位按键',23)
f.rect((725,90,1190,290),'#EFF4F4');f.text(755,110,'STM32F407ZGT6',29,bold=True)
f.text(755,159,'25  NRST',27,mono=True);f.text(755,221,'低电平有效',24)
f.text(25,300,'按下：NRST 拉低；松开：上拉恢复高电平。',24)
f.save('05_复位电路')

f=Fig(1200,790)
f.rect((445,95,755,685),'#EFF4F4');f.text(600,112,'STM32F407ZGT6',25,bold=True,anchor='mt')
# Power pins and decoupling.
f.text(462,174,'VDD / VDDA\nVBAT',20);f.line([(50,201),(445,201)])
f.text(65,160,'3.3 V',25,bold=True);f.dot(205,201);f.cap(205,201,'100 nF / VDD')
f.text(462,339,'VSS / VSSA',22);f.line([(350,355),(445,355)]);f.ground(350,355)
f.text(462,444,'VCAP1',22);f.line([(295,462),(445,462)]);f.cap(295,462,'2.2 μF')
f.text(462,559,'VCAP2',22);f.line([(295,577),(445,577)]);f.cap(295,577,'2.2 μF')
f.text(462,652,'PDR_ON',21);f.line([(380,670),(445,670)]);f.text(345,642,'3.3 V',20)
# HSE crystal with load capacitors.
f.text(738,174,'PH0\nOSC_IN',20,anchor='rt');f.text(738,279,'PH1\nOSC_OUT',20,anchor='rt')
f.line([(755,200),(890,200),(890,244)]);f.line([(755,306),(890,306),(890,270)])
f.line([(860,244),(920,244)],width=3);f.rect((860,251,920,263),'white',TEAL);f.line([(860,270),(920,270)],width=3)
f.text(939,245,'8 MHz',23)
f.line([(890,200),(1030,200)]);f.cap(1030,200,'22 pF')
f.line([(890,306),(1030,306)]);f.cap(1030,306,'22 pF')
f.dot(890,200);f.dot(890,306)
# Boot and reset.
f.text(738,419,'BOOT0',21,anchor='rt');f.line([(755,435),(910,435)]);f.resistor(910,435,label='10 kΩ');f.ground(910,510)
f.text(738,554,'NRST',21,anchor='rt');f.line([(755,571),(925,571)]);f.text(938,553,'接图 5 复位电路',21)
f.text(738,614,'PA13 / PA14',21,anchor='rt');f.line([(755,632),(900,632)]);f.text(910,605,'SWDIO / SWCLK',20)
f.text(910,641,'调试器共地',20)
f.text(12,729,'VBAT 无电池时接 3.3 V；电源入口另设储能电容。',24)
f.text(12,764,'SWD 接口引出 3.3 V 参考、GND、SWDIO、SWCLK 和 NRST。',23)
f.save('06_最小系统')

f=Fig(1200,190)
labels=['装载 MSP','Reset_Handler','SystemInit','__main','main']
for i,t in enumerate(labels):
    x=5+i*241;f.box(x,20,220,95,t)
    if i<4:f.arrow([(x+220,67),(x+241,67)])
f.text(838,142,'复制 .data，清零 .bss',24,anchor='mt')
f.save('07_启动流程')
print('Created 7 figures')
