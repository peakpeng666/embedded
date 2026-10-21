#!/usr/bin/env python3
"""Create the experiment design and circuit drawings as a four-page PDF."""
from pathlib import Path
import json
import os
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "docs/lab1_design.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
def available_font(paths):
    for path in paths:
        if Path(path).is_file():
            return str(path)
    raise RuntimeError("Required system font missing; use the prebuilt docs/lab1_design.pdf or install a Chinese TrueType font.")
pdfmetrics.registerFont(TTFont("CJK", available_font([
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", windows_fonts / "simsun.ttc"]), subfontIndex=0))
pdfmetrics.registerFont(TTFont("Latin", available_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", windows_fonts / "arial.ttf"])))
W, H = landscape(A4)
NAVY = colors.HexColor("#17354a")
TEAL = colors.HexColor("#087f8c")
GRAY = colors.HexColor("#607584")
PALE = colors.HexColor("#eef5f7")
c = canvas.Canvas(str(OUTPUT), pagesize=(W, H))
c.setTitle("实验1：查询与外部中断 - 单灯验证")
c.setAuthor("STM32L4 实验项目")
manifest = json.loads((ROOT / "build/validation.json").read_text(encoding="utf-8"))
hardware_path = ROOT.parent / "docs/hardware_validation.json"
hardware = json.loads(hardware_path.read_text(encoding="utf-8")) if hardware_path.exists() else {}
if hardware.get("image_sha256") != manifest["sha256"]:
    hardware = {}  # A prior firmware's measurements must not label a new image.


def runs(value):
    groups = []
    for char in value:
        font = "Latin" if ord(char) < 0x2e80 else "CJK"
        if groups and groups[-1][0] == font:
            groups[-1] = (font, groups[-1][1] + char)
        else:
            groups.append((font, char))
    return groups


def rich(value):
    return "".join(
        f'<font name="{font}">{escape(chunk).replace(chr(10), "<br/>")}</font>'
        for font, chunk in runs(value)
    )


def text(x, y, value, size=10, color=NAVY, align="left"):
    c.setFillColor(color)
    pieces = runs(value)
    width = sum(pdfmetrics.stringWidth(chunk, font, size) for font, chunk in pieces)
    if align == "center":
        x -= width / 2
    elif align == "right":
        x -= width
    for font, chunk in pieces:
        c.setFont(font, size)
        c.drawString(x, y, chunk)
        x += pdfmetrics.stringWidth(chunk, font, size)


def para(value, x, y, width, size=10.5, color=NAVY):
    style = ParagraphStyle("body", fontName="CJK", fontSize=size,
                           leading=size * 1.45, textColor=color, wordWrap="CJK")
    p = Paragraph(rich(value), style)
    _, height = p.wrap(width, H)
    p.drawOn(c, x, y - height)
    return y - height - 10


def header(page, title, subtitle):
    c.setFillColor(NAVY)
    c.rect(0, H - 10, W, 10, fill=1, stroke=0)
    text(38, H - 49, title, 22)
    text(38, H - 72, subtitle, 10, GRAY)
    c.setStrokeColor(colors.HexColor("#cbd8df"))
    c.line(38, 39, W - 38, 39)
    text(38, 23, "2026-10-20 | 单灯验证版；不计作 2～8 颗独立 LED 的实物验收", 8, GRAY)
    text(W - 38, 23, f"{page} / 4", 9, GRAY, "right")


def table(rows, x, top, widths, font_size=10):
    style = ParagraphStyle("cell", fontName="CJK", fontSize=font_size,
                           leading=font_size * 1.45, wordWrap="CJK")
    cells = [[Paragraph(rich(str(value)), style) for value in row] for row in rows]
    t = Table(cells, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), .8, TEAL),
        ("LINEBELOW", (0, 1), (-1, -1), .35, colors.HexColor("#d5e0e5")),
    ]))
    _, height = t.wrap(sum(widths), H)
    t.drawOn(c, x, top - height)
    return top - height


def wire(*points):
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.1)
    for a, b in zip(points, points[1:]):
        c.line(*a, *b)


def node(x, y):
    c.setFillColor(NAVY)
    c.circle(x, y, 2, stroke=0, fill=1)


def ground(x, y):
    wire((x, y), (x, y - 8))
    for dy, half in ((8, 10), (12, 6), (16, 2)):
        wire((x - half, y - dy), (x + half, y - dy))


def power(x, y, label="3.3 V"):
    wire((x, y), (x, y + 8), (x - 4, y + 3))
    wire((x, y + 8), (x + 4, y + 3))
    text(x, y + 15, label, 9, align="center")


def resv(x, top, bottom, label):
    mid = (top + bottom) / 2
    wire((x, top), (x, mid + 12))
    wire((x, mid - 12), (x, bottom))
    c.rect(x - 5, mid - 12, 10, 24, fill=0, stroke=1)
    text(x + 11, mid - 3, label, 9)


def resh(left, right, y, label):
    mid = (left + right) / 2
    wire((left, y), (mid - 17, y))
    wire((mid + 17, y), (right, y))
    c.rect(mid - 17, y - 5, 34, 10, fill=0, stroke=1)
    text(mid, y + 13, label, 9, align="center")


def capacitor(x, top, bottom, label):
    mid = (top + bottom) / 2
    wire((x, top), (x, mid + 3))
    wire((x - 8, mid + 3), (x + 8, mid + 3))
    wire((x - 8, mid - 3), (x + 8, mid - 3))
    wire((x, mid - 3), (x, bottom))
    text(x + 12, mid - 3, label, 9)


def button(x, top, bottom, label):
    mid = (top + bottom) / 2
    wire((x, top), (x, mid + 10))
    wire((x, mid - 10), (x, bottom))
    c.circle(x, mid + 10, 2, fill=0)
    c.circle(x, mid - 10, 2, fill=0)
    wire((x + 4, mid - 10), (x + 12, mid + 10))
    text(x - 13, mid - 3, label, 10, align="right")


def box(x, y, width, height, title):
    c.setFillColor(PALE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.rect(x, y, width, height, fill=1, stroke=1)
    text(x + width / 2, y + height - 24, title, 12, align="center")


header(1, "实验 1  /  查询与外部中断：七色轮闪", "STM32L496VET6 · 潘多拉开发板 · 单颗 RGB 的七种基本颜色组合")
y = para("实验目标：KEY0 用主循环查询检测，启动红、绿、蓝、黄、青、紫、白七色轮闪；KEY1 用外部中断检测，让全部颜色熄灭。再按 KEY0，从红色重新开始。", 40, 491, 760, 12)
table([
    ["操作", "输出组合", "节奏 / 说明"],
    ["上电", "OFF：灯灭", "-"],
    ["KEY0 按下", "COLOR：七色依次亮，每色之间有熄灭间隔", "亮/灭各 300 ms"],
    ["KEY1 按下", "OFF：红、绿、蓝三路全部关闭", "消抖 20 ms 后"],
    ["再按 KEY0", "从红色重新开始整组轮闪", "长按不连发"],
    ["按住 KEY1", "保持关闭，期间 KEY0 不能启动；松开不自动亮", "停止键优先"],
], 40, 429, [135, 270, 85])
text(555, 415, "实现要点", 15, TEAL)
y = 391
for value in [
    "KEY0：每 5 ms 查询 PD10；不启用 EXTI10。",
    "KEY1：PD9 映射 EXTI9；中断只记录边沿、时刻和电平。",
    "两键均消抖 20 ms；长按不连发，松开后才能再次触发。",
    "灯序按 SysTick 毫秒时间推进；ISR 内没有延时或串口打印。",
    "停止键按住时保持灭灯；必须释放后重新按 KEY0 才启动。",
]:
    y = para(value, 555, y, 244, 10.5)
para("颜色组合：红 = R，绿 = G，蓝 = B，黄 = R+G，青 = G+B，紫/品红 = R+B，白 = R+G+B。每帧 300 ms，完整一轮含 14 帧，共 4.2 s。现有硬件是一颗 RGB，用户选择单灯验证，不计作多颗独立 LED 的实物验收。", 40, 151, 760, 10.5)
para("中断是 CPU 响应按键事件的机制；本程序指定它执行灭灯动作。无需外接器材，保持现有供电和跳线。", 40, 82, 760, 10.5, TEAL)
c.showPage()

header(2, "最小系统图", "按 STM32L496 整理的功能示意；现板已具备相应供电、复位与调试电路")
box(327, 130, 184, 350, "STM32L496VET6")
text(419, 422, "VDD（全部）", 10, align="center")
text(419, 382, "VDDA / VREF+", 10, align="center")
text(419, 342, "VDDUSB / VBAT", 10, align="center")
text(419, 283, "内部 HSI16", 13, TEAL, "center")
text(419, 262, "SYSCLK = 16 MHz", 10, align="center")
text(419, 242, "本实验不使用外部晶振", 9, align="center")
text(419, 154, "VSS / VSSA（全部）", 10, align="center")
box(68, 420, 104, 44, "板载 3.3 V LDO")
text(68, 488, "USB_COM 供电", 11, TEAL)
wire((42, 440), (68, 440))
text(41, 451, "5 V", 9)
wire((172, 440), (279, 440), (279, 347))
power(279, 440)
for yy in (427, 387, 347):
    wire((279, yy), (327, yy))
    node(279, yy)
wire((216, 440), (216, 425))
node(216, 440)
capacitor(216, 425, 378, "100 nF")
ground(216, 378)
para("每个 VDD 就近一颗 100 nF；电源入口加 4.7 µF。VDDA/VREF+ 就近 100 nF + 1 µF。", 48, 339, 237, 10)
para("VBAT 无独立电池时接 3.3 V。VDDUSB 接 3.3 V。全部电源与地引脚必须连接。", 48, 258, 237, 10)
wire((327, 159), (278, 159))
ground(278, 159)
text(500, 438, "NRST", 9, align="right")
wire((511, 427), (616, 427), (733, 427))
node(616, 427)
resv(616, 480, 427, "10 kΩ")
power(616, 480)
capacitor(616, 427, 356, "100 nF")
ground(616, 356)
button(733, 427, 356, "RESET")
ground(733, 356)
text(500, 300, "BOOT0", 9, align="right")
wire((511, 289), (616, 289))
resv(616, 289, 234, "10 kΩ")
ground(616, 234)
para("等效正常启动配置；实板保持当前 BOOT 跳线，不需要改接。", 673, 285, 123, 9.5)
box(588, 112, 211, 87, "板载 CMSIS-DAP")
text(598, 151, "PA13 ↔ SWDIO    PA14 ↔ SWCLK", 9)
text(598, 133, "NRST、GND；3.3 V 作参考电压", 9)
wire((511, 185), (588, 185))
text(531, 194, "SWD", 9)
para("此图表达实验所需最小连接，不替代整板原理图；不要求另外接电源或给现板补焊电容。", 40, 83, 760, 10)
c.showPage()

header(3, "单灯验证电路图", "板载共阳 RGB 三路组合成七色；两键低有效；元件值参考原厂 V2.4 LED / KEY 网络")
box(344, 155, 168, 322, "STM32L496VET6")
text(362, 399, "PD10 / KEY0", 10)
text(362, 379, "查询，每 5 ms", 9, TEAL)
text(362, 219, "PD9 / KEY1", 10)
text(362, 199, "EXTI9 外部中断", 9, TEAL)
for yy, label in ((403, "KEY0"), (223, "KEY1")):
    wire((172, yy), (344, yy))
    node(172, yy)
    resv(172, yy + 60, yy, "10 kΩ")
    power(172, yy + 60)
    button(172, yy, yy - 58, label)
    ground(172, yy - 58)
    text(207, yy - 23, "松开 = 1；按下 = 0", 9, GRAY)
for yy, pin, resistor, label, color in (
    (402, "PE7", "R38 1 kΩ", "R", "#c64242"),
    (312, "PE8", "R43 1 kΩ", "G", "#237f4e"),
    (222, "PE9", "R52 1 kΩ", "B", "#276cb8"),
):
    text(478, yy + 13, pin, 10)
    wire((512, yy), (539, yy))
    resh(539, 628, yy, resistor)
    wire((628, yy), (674, yy))
    # LED anode is on the 3.3 V side; cathode/bar faces the GPIO resistor.
    wire((674, yy - 10), (674, yy + 10))
    p = c.beginPath()
    p.moveTo(674, yy)
    p.lineTo(695, yy + 10)
    p.lineTo(695, yy - 10)
    p.close()
    c.setFillColor(colors.HexColor(color))
    c.drawPath(p, fill=1, stroke=1)
    wire((695, yy), (766, yy))
    node(766, yy)
    for offset in (0, 9):
        wire((690 + offset, yy + 15), (701 + offset, yy + 26))
        wire((701 + offset, yy + 26), (697 + offset, yy + 25))
        wire((701 + offset, yy + 26), (700 + offset, yy + 22))
    text(729, yy + 13, label, 12, colors.HexColor(color))
wire((766, 222), (766, 452))
power(766, 452)
c.setDash(3, 3)
c.setStrokeColor(GRAY)
c.rect(651, 185, 142, 260, fill=0, stroke=1)
c.setDash()
text(652, 483, "RGB：单封装，三通道", 10, TEAL)
text(535, 161, "GPIO 输出 0 点亮；输出 1 熄灭", 10)
para("PE7、PE8、PE9 分别控制 R、G、B，低电平点亮，高电平关闭。三路独立组合形成七色，每路有板载 1 kΩ 限流电阻。", 40, 123, 755, 10)
para("串口观察：PA9(T) ↔ RXD；PA10(R) ↔ TXD；USB_COM → 电脑；115200 / 8N1、无流控。", 40, 84, 755, 10)
c.showPage()

header(4, "验证记录与回退", "电脑端测试、实板测试和回退分别记录；以原始日志作为依据")
table([
    ["已完成项目", "结果"],
    ["ARM 编译", "GCC Arm 10.3.1；-Wall -Wextra -Werror；构建通过"],
    ["六组行为测试", "消抖、长按、七色及暗间隔、IRQ 停灯依赖、停止键优先、计时回绕通过"],
    ["运行时检查", "电脑端 AddressSanitizer / UndefinedBehaviorSanitizer 通过"],
    ["镜像与向量检查", f"应用 0x08010000；{manifest['image_bytes']} 字节；栈顶 0x20010000"],
    ["烧录与保护", hardware.get("flash_summary", "单灯版本尚待烧录验证")],
    ["实际回退试验", "恢复原 512 KiB 后逐字节一致；RT-Thread 4.0.1 串口与初始化通过"],
], 40, 491, [167, 593], 10)
text(40, 241, "单灯实板结果", 14, TEAL)
para(hardware.get("physical_summary", "KEY0 七色轮闪、KEY1 全灭、长按和串口输入：等待实板记录。"), 40, 222, 760, 10.5)
text(40, 136, "资料与版本边界", 13, TEAL)
para("V2.4 原厂图公开镜像标注 STM32L475/ST-Link，实板为 STM32L496/CMSIS-DAP；软件采用 ST 官方 L496 定义。本报告是用户确认的单灯验证版，后续若扩展至多颗 LED，需要更新电路、GPIO 分配并重新验收。", 40, 117, 760, 9)
text(40, 62, "来源：ST STM32L496 数据手册与 CMSIS；Arm CMSIS 5.9.0；原厂 Pandora V2.4 SCH（公开镜像）。", 8.5, GRAY)
c.linkURL("https://www.st.com/resource/en/datasheet/stm32l496ve.pdf", (40, 58, 280, 74), relative=0)
c.linkURL("https://github.com/TrekMax/Pandora_STM32L475_Zephyr/tree/main_v3.4/docs/Hardware", (500, 58, 800, 74), relative=0)
c.save()
print(OUTPUT)
