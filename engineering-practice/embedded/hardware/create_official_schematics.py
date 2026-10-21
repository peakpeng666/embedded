#!/usr/bin/env python3
"""Assemble two A3 sheets from the vendor's actual vector schematics.

No circuit is reconstructed from a screenshot: show_pdf_page keeps the
manufacturer's original PDF paths, symbols, net names, and component values.
"""
from io import BytesIO
import hashlib
import json
from pathlib import Path

import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'hardware/sources/ALIENTEK_Pandora_official/Pandora_STM32L4_Board_V3.4_sch.pdf'
GUIDE = ROOT / 'hardware/sources/ALIENTEK_Pandora_STM32L4_Manual_V1.1.pdf'
OUT = ROOT / 'output/pdf'
OUT.mkdir(parents=True, exist_ok=True)
W, H = landscape(A3)
pdfmetrics.registerFont(TTFont('CJK', r'C:\Windows\Fonts\msyh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('Latin', r'C:\Windows\Fonts\arial.ttf'))
NAVY = colors.HexColor('#17384b')
TEAL = colors.HexColor('#087e8b')
INK = colors.HexColor('#243848')
GRAY = colors.HexColor('#526470')
LINE = colors.HexColor('#c3cfd5')
PALE = colors.HexColor('#eef4f7')
stream = BytesIO()
c = canvas.Canvas(stream, pagesize=(W, H))
overlays = []

def text(x, y, value, size=11, color=INK, font='CJK'):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, H-y, value)

def para(x, y, width, value, size=10.5, color=INK):
    style = ParagraphStyle('body', fontName='CJK', fontSize=size,
                           leading=size*1.48, textColor=color)
    p = Paragraph(value, style)
    _, height = p.wrap(width, H)
    p.drawOn(c, x, H-y-height)
    return height

def rect(x, y, width, height, fill=None):
    c.setStrokeColor(LINE)
    if fill is not None:
        c.setFillColor(fill)
    c.rect(x, H-y-height, width, height, stroke=1, fill=fill is not None)

def panel(x, y, width, height, title):
    rect(x, y, width, height)
    rect(x, y, width, 27, PALE)
    text(x+12, y+18, title, 11.5, NAVY)

def source_panel(page, x, y, width, height, title, clip, bottom=8, source_page=None):
    panel(x, y, width, height, title)
    overlays.append((page, page if source_page is None else source_page,
                     (x+7, y+34, x+width-7, y+height-bottom), clip))

def header(index, title, subtitle):
    text(32, 30, 'ALIENTEK PANDORA / STM32L496VET6', 10, TEAL, 'Latin')
    text(32, 66, title, 25, NAVY)
    text(32, 92, subtitle, 11, GRAY)
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.5)
    c.line(32, H-108, W-32, H-108)

def footer(index):
    c.setStrokeColor(LINE)
    c.setLineWidth(.5)
    c.line(32, 38, W-32, 38)
    text(32, H-23, '来源：正点原子官方下载中心“新资料”；V3.4 原理图第 1-2 页；开发指南 V1.1，PDF 第 18、23、27 页。', 8.5, GRAY)
    text(W-170, H-23, f'2026-10-21  /  {index} of 2', 8.5, GRAY, 'Latin')
    c.linkURL('http://www.openedv.com/docs/boards/iot/zdyz_panduola.html', (32, 12, W-220, 33))

header(1, '最小系统图：电源、时钟、启动与复位',
       '官方 V3.4 原始矢量电路摘编；目标 MCU 为 LQFP100，实板读得 512 KiB Flash。')
para(32, 117, W-64,
     '型号核对：配套官方开发指南明确 U3 为 STM32L496VET6；原厂 V3.4 图的 U3 文字仍沿用 STM32L475VET6，下面保留原图并注明差异。', 10.5)
source_panel(0, 32, 150, 828, 496, '01 / U3 主控、电源去耦与外部时钟（原厂整块 MCU 电路）',
             (21, 217, 635, 579))
source_panel(0, 880, 150, W-912, 174, '02 / 5 V 输入与 3.3 V 电源',
             (580, 15, 819, 164), source_page=1)
source_panel(0, 880, 338, W-912, 147, '03 / BOOT 选择',
             (635, 348, 819, 442))
source_panel(0, 880, 499, W-912, 147, '04 / 低有效复位',
             (635, 443, 819, 537))
panel(32, 666, W-64, 126, 'L496 / LQFP100 对照与本次运行设置')
para(45, 703, 545,
     '数字电源：VDD = 11 / 28 / 50 / 75 / 100；VSS = 10 / 27 / 49 / 74 / 99。<br/>'
     'VBAT = 6；VDDA = 22；VSSA = 19；VREF+ = 21；VREF- = 20；VDDUSB = 73。<br/>'
     '原图 C37-C41 为 100 nF 去耦；电源脚及电容须结合原厂完整图核对。<br/>'
     '本例使用内部 HSI16，系统与总线均为 16 MHz；原图外部时钟保留。', 10)
para(620, 703, 290,
     'NRST = 14；PH3 / BOOT0 = 94。<br/>'
     'PA13 / SWDIO = 72；PA14 / SWCLK = 76。<br/>'
     'VREF+ 经 R13 = 10 Ω 接至 VDDA；<br/>'
     '原图旁注误写 R18，按器件标注整理。', 10)
overlays.append((0, 0, (930, 703, W-45, 780), (680, 260, 809, 337)))
footer(1)
c.showPage()

header(2, '实验电路图：RGB、按键、调试与串口',
       '原厂元件编号与网络名保持完整；左侧表格把电路网络映射到本次固件使用的 L496 引脚。')
para(32, 117, W-64,
     '实板连接已验证：USB_COM → ATK CMSIS-DAP + COM3；Keil 下载与校验通过，MobaXterm 以 115200 / 8N1 / 无流控收到 STATUS。', 10.5)
source_panel(1, 32, 150, 215, 260, '01 / 共阳 RGB，低电平亮',
             (21, 271, 132, 371))
source_panel(1, 265, 150, 347, 260, '02 / 低有效按键，10 kΩ 上拉',
             (132, 271, 291, 371))
source_panel(1, 632, 150, W-664, 365, '03 / DAP、目标 SWD 与 USART1 跳线（J1）',
             (21, 15, 387, 270))
source_panel(1, 632, 533, W-664, 220, '04 / USB_DAP Type-C 接口',
             (581, 164, 819, 300))
panel(32, 432, 580, 321, '固件 / 电路网络 / LQFP100 引脚')
rows = [
    ('LED_R / R39 = 1 kΩ', 'PE7 / 38', '红色，写 0 点亮'),
    ('LED_G / R41 = 1 kΩ', 'PE8 / 39', '绿色，写 0 点亮'),
    ('LED_B / R47 = 1 kΩ', 'PE9 / 40', '蓝色，写 0 点亮'),
    ('KEY0 / R45 = 10 kΩ', 'PD10 / 57', '查询启动七色轮闪'),
    ('KEY1 / R42 = 10 kΩ', 'PD9 / 56', 'EXTI9_5 中断停止'),
    ('UART1_TX', 'PA9 / 68', 'MCU TX → DAP 接收'),
    ('UART1_RX', 'PA10 / 69', 'MCU RX ← DAP 发送'),
    ('T_JTMS / SWDIO', 'PA13 / 72', '目标 MCU 的 SWD 数据'),
    ('T_JTCK / SWCLK', 'PA14 / 76', '目标 MCU 的 SWD 时钟'),
    ('RESET / NRST', 'NRST / 14', '目标 MCU 低有效复位'),
]
for i, row in enumerate(rows):
    y = 478+i*23
    if i % 2 == 0:
        c.setFillColor(colors.HexColor('#f5f8fa'))
        c.rect(40, H-y-16, 564, 23, stroke=0, fill=1)
    for x, value in zip((47, 275, 395), row):
        text(x, y+9, value, 9.5)
para(42, 720, 560,
     'KEY2 / PD8 与 WK_UP / PC13 未用于本例。原图 J2 是 DAP 控制器自身的调试接口；连接目标板开发使用 USB_COM。', 9.5)
para(32, 765, W-64,
     '电路核对依据：原厂 V3.4 电路网络 + 配套 L496 开发指南 + ST DS11585 Rev20 的 LQFP100 引脚定义。本图摘取本实验所需电路，完整两页原理图另存于 hardware/sources/ALIENTEK_Pandora_official。', 9.5, GRAY)
footer(2)
c.save()

layout = fitz.open(stream=stream.getvalue(), filetype='pdf')
original = fitz.open(SOURCE)
vendor = fitz.open()
# The original PDF leaves several fonts unembedded. Preserve its vector
# geometry and outline its glyphs so the extracted sheets print consistently.
for source_page in original:
    svg = source_page.get_svg_image(text_as_path=True)
    converted = fitz.open(stream=svg.encode('utf-8'), filetype='svg')
    vendor.insert_pdf(fitz.open(stream=converted.convert_to_pdf(), filetype='pdf'))
for index, source_index, area, clip in overlays:
    layout[index].show_pdf_page(fitz.Rect(area), vendor, source_index,
                                clip=fitz.Rect(clip), keep_proportion=True)
layout.set_metadata({
    'title': '正点原子潘多拉 STM32L496VET6 最小系统与实验电路（官方图核对版）',
    'author': '电路来源：正点原子官方资料；本工程整理与实板对照',
    'subject': 'V3.4 官方矢量原理图；MCU 型号依官方 L496 开发指南核对',
    'keywords': 'Pandora STM32L496VET6 CMSIS-DAP UART RGB EXTI V3.4',
})
destination = OUT / 'STM32L496_minimal-system-and-experiment-circuit_official-drawing.pdf'
layout.save(destination, garbage=4, deflate=True)
for i, page in enumerate(layout):
    name = ('01_minimal-system-diagram', '02_experiment-circuit')[i]
    (OUT / f'{name}.svg').write_text(page.get_svg_image(), encoding='utf-8')
    page.get_pixmap(dpi=220).save(OUT / f'{name}.png')

catalog = {
    'checked_at': '2026-10-21',
    'vendor_download_page': 'http://www.openedv.com/docs/boards/iot/zdyz_panduola.html',
    'vendor_discussion_page': 'http://www.openedv.com/thread-284556-1-1.html',
    'vendor_quark_share': 'https://pan.quark.cn/s/65fa193e56a3',
    'vendor_quark_passcode': 'dhFn',
    'vendor_baidu_share': 'https://pan.baidu.com/s/17T9ZlkHhXO7ZF1ixRkGCEQ',
    'vendor_baidu_passcode': 'mznq',
    'path_on_share': '【正点原子】潘多拉IoT开发板/【正点原子】潘多拉IoT开发板资料（新资料）',
    'guide_l496_identity_pdf_pages': [18, 23, 27, 52, 65],
    'schematic_filename': SOURCE.name,
    'schematic_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'guide_sha256': hashlib.sha256(GUIDE.read_bytes()).hexdigest(),
    'match': '官方同产品新版资料；指南明确 STM32L496VET6；V3.4 电路含 DAP、Type-C 与本次使用的相同引脚网络。',
    'limits': 'V3.4 原图 U3 文字仍为 STM32L475VET6；保留原始标注。没有通过软件确认 PCB 丝印版本，V3.4 为接口特征最匹配的官方图。',
    'st_datasheet': 'https://www.st.com/resource/en/datasheet/stm32l496ve.pdf',
    'st_datasheet_pinout_pdf_page': 68,
    'output': str(destination.relative_to(ROOT)),
    'output_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
}
(ROOT / 'hardware/official_sources.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(destination), 'pages': len(layout), 'page_size': list(layout[0].rect), 'source_sha256': catalog['schematic_sha256']}, ensure_ascii=False, indent=2))
