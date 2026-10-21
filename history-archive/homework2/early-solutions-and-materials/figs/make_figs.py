# -*- coding: utf-8 -*-
"""生成《嵌入式系统原理及应用》作业 2026-09-29 的 6 张插图"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
OUT = r"D:\Peak\Desktop\嵌入式\03_作业_2026-09-29\figs"

BLUE, ORANGE, GREEN, RED, PURPLE, GRAY = '#4C78A8', '#F58518', '#54A24B', '#D4544F', '#B279A2', '#8C8C8C'
DARK = '#2F2F2F'

def rbox(ax, x, y, w, h, fc, ec, lw=1.6, rad=0.06, z=2):
    b = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.012,rounding_size={rad}",
                       fc=fc, ec=ec, lw=lw, zorder=z, mutation_aspect=1)
    ax.add_patch(b); return b

def arrow(ax, x0, y0, x1, y1, color=DARK, lw=1.8, style='-|>', ls='-'):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, linestyle=ls,
                                shrinkA=0, shrinkB=0), zorder=3)

def line(ax, x0, y0, x1, y1, color=DARK, lw=1.6, ls='-'):
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls, zorder=2)

# ============================================================ 图2-1 存储器映射
fig, ax = plt.subplots(figsize=(10.6, 11.2))
ax.set_xlim(0, 10.6); ax.set_ylim(-0.55, 10.9); ax.set_axis_off()
X0, W = 1.3, 2.9                       # 存储器主柱
regions = [  # (y底, 高度GB, 颜色, 区名, 范围, 大小)
    (0.0, 0.5, BLUE,   "Code 代码区",     "0x0000 0000 ~ 0x1FFF FFFF", "512MB"),
    (0.5, 0.5, ORANGE, "SRAM 区",         "0x2000 0000 ~ 0x3FFF FFFF", "512MB"),
    (1.0, 0.5, GREEN,  "片上外设区",      "0x4000 0000 ~ 0x5FFF FFFF", "512MB"),
    (1.5, 1.0, GRAY,   "External RAM",    "0x6000 0000 ~ 0x9FFF FFFF", "1GB"),
    (2.5, 1.0, GRAY,   "External Device", "0xA000 0000 ~ 0xDFFF FFFF", "1GB"),
    (3.5, 0.5, RED,    "私有外设(系统)区","0xE000 0000 ~ 0xFFFF FFFF", "512MB"),
]
scale = 10.0 / 4.0                      # 4GB -> 10
for yb, gb, c, name, rng, size in regions:
    y, h = yb * scale, gb * scale
    ax.add_patch(Rectangle((X0, y), W, h, fc=c, ec=DARK, lw=1.4, alpha=0.82, zorder=2))
    ax.text(X0 + W / 2, y + h * 0.66, name, ha='center', va='center',
            fontsize=10, color='white', weight='bold', zorder=3)
    ax.text(X0 + W / 2, y + h * 0.40, rng, ha='center', va='center',
            fontsize=8.5, color='white', zorder=3)
    ax.text(X0 + W / 2, y + h * 0.16, f"（{size}）", ha='center', va='center',
            fontsize=8.3, color='white', zorder=3)
    ax.text(X0 - 0.18, y, rng.split('~')[0].strip(), ha='right', va='center', fontsize=8.5, color=DARK)
ax.text(X0 - 0.18, 10.0, "0xFFFF FFFF", ha='right', va='center', fontsize=8.5, color=DARK)
# ★ 外设区红框高亮 + 星标
ax.add_patch(Rectangle((X0, 1.0 * scale), W, 0.5 * scale, fc='none', ec=RED, lw=3.0, zorder=4))
ax.add_patch(Rectangle((X0, 3.5 * scale), W, 0.5 * scale, fc='none', ec=RED, lw=3.0, zorder=4))
# 右侧两个放大面板（绿上、红下错开，避免长引线交叉）
p1 = rbox(ax, 5.3, 4.1, 5.0, 2.9, '#EDF5EC', GREEN, lw=1.8)
ax.text(7.8, 6.55, "片上外设区放大（0x4000 0000 起）", ha='center', fontsize=11, weight='bold', color=GREEN)
for i, t in enumerate([
    "★ GPIOA ~ GPIOI   0x4002 0000 起（AHB1 总线）",
    "★ TIM2            0x4000 0000 起（APB1 总线）",
    "★ CAN1 / CAN2     0x4000 6400 / 0x4000 6800（APB1）",
    "    RCC 复位与时钟 0x4002 3800（AHB1）",
    "    USART1         0x4001 1000（APB2 总线）"]):
    ax.text(5.55, 6.05 - i * 0.42, t, ha='left', fontsize=9.5,
            color=RED if t.startswith('★') else DARK, weight='bold' if t.startswith('★') else 'normal')
arrow(ax, X0 + W, 1.25 * scale, 5.3, 5.2, color=GREEN)
p2 = rbox(ax, 5.3, 7.8, 5.0, 2.5, '#FBEDEC', RED, lw=1.8)
ax.text(7.8, 9.85, "私有外设区放大（0xE000 0000 起）", ha='center', fontsize=11, weight='bold', color=RED)
for i, t in enumerate([
    "★ SysTick  0xE000 E010（24 位系统节拍定时器）",
    "    NVIC     0xE000 E100（嵌套向量中断控制器）",
    "    SCS 系统控制空间 0xE000 E000~0xE000 EFFF"]):
    ax.text(5.55, 9.3 - i * 0.42, t, ha='left', fontsize=9.5,
            color=RED if t.startswith('★') else DARK, weight='bold' if t.startswith('★') else 'normal')
arrow(ax, X0 + W, 3.75 * scale, 5.3, 8.9, color=RED)
ax.text(5.3, 2.9, "注：Cortex-M4 为 32 位处理器，4GB 线性地址空间按 512MB/1GB 分区；\n普通片上外设从 0x4000 0000 起，内核私有外设（SysTick/NVIC/SCS）在 0xE000 0000 之后。",
        ha='left', fontsize=9.5, color=DARK)
ax.text(5.3, 1.5, "（灰色两区由 FSMC 外扩存储器使用）", ha='left', fontsize=9, color='#666666')
ax.set_title("图 2-1  ARM Cortex-M4 存储器映射（4GB 地址空间划分，★为本题外设）", fontsize=14, weight='bold', pad=14)
plt.tight_layout(); plt.savefig(f"{OUT}/fig_q2_memory_map.png", dpi=200, bbox_inches='tight'); plt.close()

# ============================================================ 图3-1 中断流程
fig, ax = plt.subplots(figsize=(11.6, 5.6))
ax.set_xlim(0, 118); ax.set_ylim(0, 54); ax.set_axis_off()
steps = [  # (x, w, 颜色, 标题, 副文本)
    (2, 16, BLUE,   "主程序\n正常运行", ""),
    (24, 18, ORANGE,"① 中断源\n请求 IRQ", "按键/定时器溢出/\nADC 转换完成…"),
    (48, 22, GREEN, "② NVIC 判优", "使能? 优先级比较?\n可抢占?（中断嵌套）"),
    (76, 20, PURPLE,"③ 硬件自动响应", "自动压栈 8 个寄存器\n（现场保护）+ 查向量表"),
    (102, 15, RED,  "④ 执行\nISR", "中断服务程序"),
]
for x, w, c, t1, t2 in steps:
    rbox(ax, x, 26, w, 16, '#F5F5F5', c, lw=2.0)
    ax.text(x + w / 2, 36.5, t1, ha='center', va='center', fontsize=10.5, weight='bold', color=c)
    if t2: ax.text(x + w / 2, 30.2, t2, ha='center', va='center', fontsize=8.6, color=DARK)
arrow(ax, 18, 34, 24, 34); arrow(ax, 42, 34, 48, 34); arrow(ax, 70, 34, 76, 34); arrow(ax, 96, 34, 102, 34)
# 返回箭头（大回环）
ax.annotate('', xy=(10, 25.4), xytext=(109.5, 25.4),
            arrowprops=dict(arrowstyle='-|>', color=RED, lw=2.0, ls='--',
                            connectionstyle='bar,fraction=-0.16'), zorder=3)
ax.text(60, 15.2, "⑤ 中断返回（异常返回）：硬件自动出栈恢复现场，若已有挂起中断则【尾链 Tail-Chaining】直接进入下一个 ISR",
        ha='center', fontsize=10, color=RED, weight='bold')
kw = rbox(ax, 2, 1.5, 115, 8.5, '#FBF3E6', ORANGE, lw=1.5)
ax.text(59.5, 5.7, "关键词：中断源 · 中断请求(IRQ) · 使能/屏蔽 · 抢占优先级 · 子优先级 · 优先级分组 · 中断嵌套 · 挂起(Pending) ·\n"
                   "现场保护（自动压栈 xPSR、PC、LR、R12、R3~R0）· 向量表查表 · ISR 中断服务程序 · 中断返回（出栈）· 尾链",
        ha='center', va='center', fontsize=9.6, color=DARK)
ax.set_title("图 3-1  ARM Cortex-M4 中断响应流程与关键概念", fontsize=14, weight='bold', pad=10)
plt.tight_layout(); plt.savefig(f"{OUT}/fig_q3_interrupt_flow.png", dpi=200, bbox_inches='tight'); plt.close()

# ============================================================ 图3-2 向量表
fig, ax = plt.subplots(figsize=(10.6, 6.4))
ax.set_xlim(0, 106); ax.set_ylim(0, 60); ax.set_axis_off()
rows = [  # (偏移, 内容, 颜色, 加粗)
    ("0x0000", "MSP 初值（主堆栈指针栈顶）", RED, True),
    ("0x0004", "Reset_Handler（复位向量）", RED, True),
    ("0x0008", "NMI 不可屏蔽中断", DARK, False),
    ("0x000C", "HardFault 硬错误", DARK, False),
    ("0x0010~0x003C", "MemManage / BusFault / UsageFault / 保留 / SVCall / DebugMon /\nPendSV / SysTick（共 16 个内核异常）", DARK, False),
    ("0x0040 起", "外设中断 IRQ0 ~ IRQ81（WWDG → FPU，共 82 个）", GREEN, True),
]
X, W, Y, RH = 2, 52, 12, 6.4
rbox(ax, X, Y - 1.2, W, RH * len(rows) + 2.6, '#FFFFFF', DARK, lw=1.8)
ax.text(X + 1.5, Y + RH * len(rows) + 0.6, "异常/中断向量表（每表项 4 字节，按异常号顺序排列）", fontsize=11, weight='bold', color=DARK)
for i, (off, txt, c, bold) in enumerate(rows):
    y = Y + RH * (len(rows) - 1 - i)
    if i < 2: ax.add_patch(Rectangle((X + 0.3, y + 0.3), W - 0.6, RH - 0.6, fc='#FBEDEC', ec='none', zorder=1))
    if i == 5: ax.add_patch(Rectangle((X + 0.3, y + 0.3), W - 0.6, RH - 0.7, fc='#EDF5EC', ec='none', zorder=1))
    ax.text(X + 2, y + RH / 2, off, ha='left', va='center', fontsize=9.6, color=c, weight='bold', zorder=2)
    ax.text(X + 16, y + RH / 2, txt, ha='left', va='center', fontsize=9.4 if len(txt) < 40 else 8.4, color=c,
            weight='bold' if bold else 'normal', zorder=2)
    if i < len(rows) - 1: line(ax, X + 1, y, X + W - 1, y, color='#CCCCCC', lw=1)
# 右侧作用面板
p = rbox(ax, 58, 14, 46, 40, '#EDF2F9', BLUE, lw=1.8)
ax.text(81, 51.0, "向量表的四大作用", ha='center', fontsize=11.5, weight='bold', color=BLUE)
for i, t in enumerate([
    "① 建立异常号 → ISR 入口地址的固定映射：",
    "    表项地址 = 表基址 + 异常号 × 4 字节",
    "② 硬件自动查表：响应时取出表项装入 PC，",
    "    直接进入 ISR —— 无需软件判断中断源",
    "    （“向量中断 vectored” 的含义）",
    "③ 表首两项特殊：0x00=MSP 初值、",
    "    0x04=复位向量 —— 上电后 CPU 自动取值，",
    "    完成复位初始化（复位序列）",
    "④ 配合硬件压栈/出栈与尾链机制，",
    "    中断响应最快仅 12 个时钟周期"]):
    ax.text(60, 47.0 - i * 3.6, t, ha='left', fontsize=9.5, color=DARK)
ax.set_title("图 3-2  异常/中断向量表的结构与作用（以 STM32F407 为例，共 98 项）", fontsize=14, weight='bold', pad=10)
plt.tight_layout(); plt.savefig(f"{OUT}/fig_q3_vector_table.png", dpi=200, bbox_inches='tight'); plt.close()

# ============================================================ 图4-1 总线矩阵
fig, ax = plt.subplots(figsize=(11.8, 7.6))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_axis_off()
masters = ["Cortex-M4 内核\nI-Bus / D-Bus / S-Bus", "DMA1\n（M/P 两端口）", "DMA2\n（M/P 两端口）", "以太网\nDMA", "USB OTG HS\nDMA"]
for i, m in enumerate(masters):
    x = 2 + i * 19.6
    rbox(ax, x, 88, 17.5, 10, '#EDF2F9', BLUE, lw=1.6)
    ax.text(x + 8.75, 93, m, ha='center', va='center', fontsize=8.8, weight='bold', color=BLUE)
    arrow(ax, x + 8.75, 87.6, x + 8.75, 81.5, color=BLUE, lw=1.5)
rbox(ax, 8, 66, 84, 15, '#F5F5F5', DARK, lw=2.2, rad=0.12)
ax.text(50, 75.5, "总线矩阵  Bus Matrix（8 条主总线 × 7 条从总线）", ha='center', fontsize=12.5, weight='bold', color=DARK)
ax.text(50, 69.5, "多主仲裁 · 并行数据通路：允许内核与 DMA 同时访问不同的从设备", ha='center', fontsize=9, color='#555555')
slaves = [("内部 Flash\nI-CODE/D-CODE\n（ART 加速）", GRAY, False),
          ("SRAM1/2 + CCM\n112+16+64 KB", GRAY, False),
          ("AHB1 外设\nGPIOA~I ★\nRCC/DMA/CRC", GREEN, True),
          ("AHB2 外设\nUSB OTG FS\nDCMI / RNG", GRAY, False),
          ("AHB3\nFSMC 外扩\n存储器/LCD", GRAY, False)]
for i, (s, c, hl) in enumerate(slaves):
    x = 2 + i * 19.6
    rbox(ax, x, 44, 17.5, 14, '#FFFFFF', c if hl else DARK, lw=2.4 if hl else 1.6)
    ax.text(x + 8.75, 51, s, ha='center', va='center', fontsize=8.9,
            color=GREEN if hl else DARK, weight='bold' if hl else 'normal')
    arrow(ax, x + 8.75, 65.6, x + 8.75, 58.6, color=DARK, lw=1.5)
# AHB1 -> 两个 APB 桥
line(ax, 61.5, 43.6, 61.5, 38, color=GREEN, lw=2.2); line(ax, 61.5, 38, 27, 38, color=GREEN, lw=2.2); line(ax, 61.5, 38, 76, 38, color=GREEN, lw=2.2)
ax.plot([61.5, 27, 76], [38, 38, 38], 'o', color=GREEN, ms=5, zorder=3)   # 分流节点
arrow(ax, 27, 38, 27, 33.5, color=GREEN, lw=2.2)
rbox(ax, 6, 8, 42, 25, '#EDF5EC', GREEN, lw=1.8)
ax.text(27, 30.2, "AHB1 → APB1 桥（最高 42MHz）", ha='center', fontsize=10, weight='bold', color=GREEN)
ax.text(8, 26.6, "★ TIM2 ~ TIM7、TIM12~14（TIM2 在此）", ha='left', fontsize=9.2, color=RED, weight='bold')
ax.text(8, 22.4, "★ CAN1 / CAN2", ha='left', fontsize=9.2, color=RED, weight='bold')
ax.text(8, 18.2, "USART2/3、UART4/5、I2C1~3、SPI2/3", ha='left', fontsize=9.2, color=DARK)
ax.text(8, 14.0, "RTC、WWDG/IWDG、DAC、PWR", ha='left', fontsize=9.2, color=DARK)
arrow(ax, 76, 38, 76, 33.5, color=GREEN, lw=2.2)
rbox(ax, 56, 8, 40, 25, '#EDF5EC', GREEN, lw=1.8)
ax.text(76, 30.2, "AHB1 → APB2 桥（最高 84MHz）", ha='center', fontsize=10, weight='bold', color=GREEN)
ax.text(58, 26.6, "★ USART1", ha='left', fontsize=9.2, color=RED, weight='bold')
ax.text(58, 22.4, "ADC1~ADC3、TIM1/TIM8/TIM9~11", ha='left', fontsize=9.2, color=DARK)
ax.text(58, 18.2, "SPI1、SPI4~6、SDIO", ha='left', fontsize=9.2, color=DARK)
ax.text(58, 14.0, "SYSCFG / EXTI（外部中断）", ha='left', fontsize=9.2, color=DARK)
ax.text(50, 3.0, "★ = 本题三个模块：GPIO 挂 AHB1；TIM2 挂 APB1（经 AHB1→APB1 桥）；USART1 挂 APB2（经 AHB1→APB2 桥）",
        ha='center', fontsize=9.8, color=RED, weight='bold')
ax.set_title("图 4-1  STM32F40x 内部总线矩阵与主/从设备（★为本题三个模块）", fontsize=14, weight='bold', pad=10)
plt.tight_layout(); plt.savefig(f"{OUT}/fig_q4_bus_matrix.png", dpi=200, bbox_inches='tight'); plt.close()

# ============================================================ 图5-1 时钟树
fig, ax = plt.subplots(figsize=(11.8, 7.2))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_axis_off()
def srcbox(y, t, c):
    rbox(ax, 2, y, 19, 9, '#FFFFFF', c, lw=1.8)
    ax.text(11.5, y + 4.5, t, ha='center', va='center', fontsize=8.8, color=c, weight='bold')
srcbox(80, "HSE 高速外部晶振\n4~26MHz（板上 8MHz）", BLUE)
srcbox(66, "HSI 内部 RC\n16MHz", BLUE)
srcbox(24, "LSE 低速外部\n32.768kHz", GRAY)
srcbox(10, "LSI 内部 RC\n≈32kHz", GRAY)
# 主 PLL
rbox(ax, 30, 60, 24, 32, '#EDF2F9', BLUE, lw=2.0)
ax.text(42, 88.2, "主 PLL 锁相环", ha='center', fontsize=10.5, weight='bold', color=BLUE)
for i, t in enumerate(["÷ M（=8）", "× N（=336）", "÷ P（=2）"]):
    rbox(ax, 34, 76.5 - i * 7.5, 16, 5.6, '#FFFFFF', BLUE, lw=1.4)
    ax.text(42, 79.3 - i * 7.5, t, ha='center', va='center', fontsize=9.6, weight='bold', color=BLUE)
ax.text(42, 61.8, "VCO | PLL-Q → USB 48MHz", ha='center', fontsize=7.8, color='#555555')
arrow(ax, 21, 84.5, 30, 84.5, color=BLUE, lw=2.0)
ax.annotate('', xy=(30, 70.5), xytext=(21, 70.5), arrowprops=dict(arrowstyle='-|>', color=BLUE, lw=1.6, linestyle='--'))
ax.text(25.5, 77.5, "HSE/HSI\n二选一", ha='center', fontsize=7.5, color=BLUE)
# SYSCLK 选择器
rbox(ax, 61, 68, 13, 16, '#FFFFFF', RED, lw=2.2)
ax.text(67.5, 79.5, "SYSCLK", ha='center', fontsize=9.6, weight='bold', color=RED)
ax.text(67.5, 75.2, "选择器 SW\n三选一", ha='center', fontsize=8.4, color=RED)
ax.text(67.5, 70.5, "≤168MHz", ha='center', fontsize=8.6, weight='bold', color=RED)
arrow(ax, 54, 84.5, 61, 79, color=RED, lw=2.0)
ax.text(55.2, 86.4, "PLLCLK", ha='left', fontsize=8.6, color=RED)
# HSE 直通旁路：从 HSE 顶部绕 PLL 上方进入 SYSCLK 顶部
line(ax, 11.5, 89, 11.5, 95, color=BLUE, lw=1.4, ls=':'); line(ax, 11.5, 95, 64, 95, color=BLUE, lw=1.4, ls=':')
arrow(ax, 64, 95, 64, 84.2, color=BLUE, lw=1.4, ls=':')
ax.text(14, 96.4, "HSE 直通（可旁路 PLL 作 SYSCLK）", ha='left', fontsize=7.5, color=BLUE)
# HSI 直通旁路：从 HSI 底部绕 PLL 下方进入 SYSCLK 左侧
line(ax, 11.5, 66, 11.5, 57, color=BLUE, lw=1.4, ls=':'); line(ax, 11.5, 57, 57.5, 57, color=BLUE, lw=1.4, ls=':')
line(ax, 57.5, 57, 57.5, 73, color=BLUE, lw=1.4, ls=':')
arrow(ax, 57.5, 73, 60.7, 73, color=BLUE, lw=1.4, ls=':')
ax.text(30, 58.3, "HSI 直通 16MHz", ha='left', fontsize=7.5, color=BLUE)
# 分频输出
outs = [(46, "AHB 分频 ÷1\nHCLK = 168MHz", "→ AHB1：GPIO、DMA、RCC", GREEN),
        (25, "APB1 分频 ÷4\nPCLK1 = 42MHz", "APB1 定时器 ×2 = 84MHz（TIM2 在此）", ORANGE),
        (4,  "APB2 分频 ÷2\nPCLK2 = 84MHz", "APB2 定时器 ×2 = 168MHz（ADC 在此）", PURPLE)]
for y, t1, t2, c in outs:
    rbox(ax, 82, y, 17, 13, '#FFFFFF', c, lw=2.0)
    ax.text(90.5, y + 9.3, t1, ha='center', va='center', fontsize=8.7, weight='bold', color=c)
    ax.text(90.5, y + 3.6, t2, ha='center', va='center', fontsize=7.2, color=DARK)
    arrow(ax, 74, 72, 82, y + 6.5, color=c, lw=1.8)
# RTC 支路
rbox(ax, 30, 8, 24, 18, '#F5F5F5', GRAY, lw=1.6)
ax.text(42, 22.5, "RTC / 备份寄存器", ha='center', fontsize=9.5, weight='bold', color='#555555')
ax.text(42, 17.5, "LSE（32.768k=2¹⁵ 分频恰为 1Hz）\n或 LSI / HSE/32", ha='center', fontsize=8.2, color=DARK)
ax.text(42, 11.5, "LSI → 独立看门狗 IWDG", ha='center', fontsize=8.4, color=DARK)
arrow(ax, 21, 28.5, 30, 20, color=GRAY, lw=1.4); arrow(ax, 21, 14.5, 30, 14.5, color=GRAY, lw=1.4)
# 公式框
rbox(ax, 30, 33, 44, 15, '#FBF3E6', ORANGE, lw=1.8)
ax.text(52, 43.5, "SYSCLK = (HSE ÷ M) × N ÷ P = 8MHz ÷ 8 × 336 ÷ 2 = 168MHz（最大值）", ha='center', fontsize=10, weight='bold', color=DARK)
ax.text(52, 37.0, "SYSCLK 三选一：HSI / HSE / PLLCLK；GPIO 时钟来自 AHB1；SysTick = AHB 或 ÷8；ADC 时钟来自 APB2", ha='center', fontsize=8.8, color=DARK)
ax.text(52, 1.2, "三个 PLL：主 PLL（SYSCLK）、I2S-PLL、SAI-PLL；IRC48M 专供 USB/RNG；MCO0/MCO1 可对外输出两路时钟",
        ha='center', fontsize=8.8, color='#555555')
ax.set_title("图 5-1  STM32F40x 时钟树：5 路时钟源 → PLL → SYSCLK → 总线分级", fontsize=14, weight='bold', pad=10)
plt.tight_layout(); plt.savefig(f"{OUT}/fig_q5_clock_tree.png", dpi=200, bbox_inches='tight'); plt.close()

# ============================================================ 图6-1 复位电路
fig, ax = plt.subplots(figsize=(8.6, 7.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_axis_off()
cx = 32                              # 主干线 x
ax.text(cx, 95.5, "VDD = 3.3V", ha='center', fontsize=11, weight='bold', color=RED)
line(ax, cx, 93, cx, 88)
# 电阻（IEC 矩形符号）
ax.add_patch(Rectangle((cx - 5, 76), 10, 12, fc='white', ec=DARK, lw=2.0))
ax.text(cx + 8, 82, "R1 = 10kΩ\n（上拉，平时保持高电平）", ha='left', va='center', fontsize=9.5, color=DARK)
line(ax, cx, 76, cx, 62)
# NRST 节点
ax.plot([cx], [62], 'o', color=DARK, ms=7)
ax.text(cx + 3, 63.8, "NRST 节点", ha='left', fontsize=9.5, color=DARK)
arrow(ax, cx, 62, 76, 62, color=RED, lw=2.2)
ax.text(78, 65.5, "→ 接 MCU 的 NRST 引脚\n（LQFP144 封装 Pin 25）", ha='left', fontsize=9.8, weight='bold', color=RED)
# 电容支路
line(ax, cx, 62, cx, 48)
ax.plot([cx - 7, cx + 7], [48, 48], color=DARK, lw=2.4)      # 上极板
ax.plot([cx - 7, cx + 7], [44.5, 44.5], color=DARK, lw=2.4)   # 下极板
ax.text(cx + 9, 46.2, "C1 = 0.1μF（100nF）", ha='left', va='center', fontsize=9.5, color=DARK)
line(ax, cx, 44.5, cx, 34)
# 按键支路（与电容并联）
bx = cx + 22
line(ax, cx, 58, bx - 8, 58); line(ax, bx + 8, 58, bx + 16, 58)
line(ax, bx + 16, 58, bx + 16, 34)
ax.plot([bx - 6, bx + 6], [60.5, 61.8], color=DARK, lw=2.2)   # 按键杠杆
ax.plot([bx - 7], [58], marker='o', color=DARK, ms=5)
ax.plot([bx + 7], [58], marker='o', color=DARK, ms=5)
ax.plot([bx - 5.5], [61.8], marker='o', color=DARK, ms=4, mfc='white')
ax.plot([bx + 5.5], [61.8], marker='o', color=DARK, ms=4, mfc='white')
ax.text(bx, 66.5, "SW1 复位按键", ha='center', fontsize=9.5, weight='bold', color=DARK)
# 地
line(ax, cx - 9, 34, bx + 16, 34)
ax.plot([cx, bx + 16], [34, 34], 'o', color=DARK, ms=5)      # 两条支路与地母线的连接点
ax.plot([cx], [58], 'o', color=DARK, ms=5)                   # SW1 支路自干线的引出节点
line(ax, cx, 34, cx, 29)
for w, y in [(9, 29), (6, 26), (3, 23)]:
    ax.plot([cx - w, cx + w], [y, y], color=DARK, lw=2.2)
ax.text(cx + 12, 25, "GND", ha='left', fontsize=10, color=DARK)
# 说明框
rbox(ax, 2, 2, 96, 15, '#EDF5EC', GREEN, lw=1.8)
ax.text(50, 12.6, "① 上电复位：上电瞬间 C1 两端电压不能突变，NRST 为低电平；随 C1 充电（τ = RC ≈ 1ms）逐渐升高，", ha='center', fontsize=9.5, color=DARK)
ax.text(50, 8.8, "    低电平保持时间远大于 20μs 的复位门限，芯片可靠复位；", ha='center', fontsize=9.5, color=DARK)
ax.text(50, 5.0, "② 手动复位：按下 SW1 将 NRST 拉到地，松开后 C1 重新充电恢复高电平。", ha='center', fontsize=9.5, color=DARK)
ax.set_title("图 6-1  NRST 典型复位电路（上电复位 + 手动复位，ST 官方推荐参数）", fontsize=13.5, weight='bold', pad=10)
plt.tight_layout(); plt.savefig(f"{OUT}/fig_q6_reset_circuit.png", dpi=200, bbox_inches='tight'); plt.close()

print("ALL FIGURES DONE")
