# -*- coding: utf-8 -*-
"""时钟之迹 PPT 插图：SysTick 原理图 + 双库初始化流程图（宽幅适配 16:9）"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

OUT = r"D:\Peak\Desktop\嵌入式\06_例程_时钟之迹\figs"
TEAL, AMBER, DARKBG, INK = '#0E7C66', '#E8A13D', '#0D1B1E', '#1A2528'
BLUE, ORANGE, GREEN, RED, PURPLE, GRAY = '#4C78A8', '#F58518', '#54A24B', '#D4544F', '#B279A2', '#8C8C8C'
DARK = '#2F2F2F'

def rbox(ax, x, y, w, h, fc, ec, lw=1.6, rad=0.045, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.008,rounding_size={rad}",
                 fc=fc, ec=ec, lw=lw, zorder=z))

def arrow(ax, x0, y0, x1, y1, color=DARK, lw=1.8, ls='-'):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=16,
                 color=color, lw=lw, linestyle=ls, zorder=3, shrinkA=2, shrinkB=2))

def line(ax, x0, y0, x1, y1, color=DARK, lw=1.6, ls='-'):
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls, zorder=2)

# ============================================================ 图A SysTick 原理
fig, ax = plt.subplots(figsize=(11.2, 4.6))
ax.set_xlim(0, 100); ax.set_ylim(0, 42); ax.set_axis_off()
# 时钟源选择
rbox(ax, 2, 16, 13, 9, '#FFFFFF', BLUE, lw=1.8)
ax.text(8.5, 22.2, "时钟源选择", ha='center', fontsize=11.5, weight='bold', color=BLUE)
ax.text(8.5, 19.2, "CTRL 控制和状态寄存器\nHCLK(168M) 或 HCLK÷8(21M)", ha='center', va='center', fontsize=9, color=DARK)
# 递减计数器
rbox(ax, 24, 13, 24, 15, '#EDF5EC', GREEN, lw=2.0)
ax.text(36, 24.6, "24 位递减计数器", ha='center', fontsize=11.5, weight='bold', color=GREEN)
ax.text(36, 20.6, "VAL  当前值\nLOAD 重装载值（ticks-1）\n过零自动重载 LOAD", ha='center', va='center', fontsize=9.3, color=DARK)
# 事件输出
rbox(ax, 57, 26.5, 19, 8.5, '#FBEDEC', RED, lw=1.8)
ax.text(66.5, 32.6, "COUNTFLAG 置 1", ha='center', fontsize=10.5, weight='bold', color=RED)
ax.text(66.5, 29.3, "轮询法读取（delay_us）", ha='center', fontsize=9, color=DARK)
rbox(ax, 57, 12.5, 19, 8.5, '#FBF3E6', ORANGE, lw=1.8)
ax.text(66.5, 18.6, "TICKINT 中断", ha='center', fontsize=10.5, weight='bold', color=ORANGE)
ax.text(66.5, 15.3, "SysTick_Handler\n（HAL_IncTick）", ha='center', fontsize=9, color=DARK)
# 滴答公式
rbox(ax, 83, 14, 15, 12, '#F5F5F7', DARK, lw=1.6)
ax.text(90.5, 23.2, "滴答时长", ha='center', fontsize=10.5, weight='bold', color=DARK)
ax.text(90.5, 18.9, "T = (LOAD+1) / f\n1ms 滴答：\nLOAD=168M/1000\n=168000-1", ha='center', va='center', fontsize=9.2, color=TEAL, weight='bold')
arrow(ax, 15, 20.5, 24, 20.5, GREEN)
arrow(ax, 48, 26, 57, 30.5, RED); arrow(ax, 48, 17, 57, 16.5, ORANGE)
arrow(ax, 76, 30.7, 83, 24.5, GRAY, ls='--'); arrow(ax, 76, 16.7, 83, 17.5, GRAY, ls='--')
ax.set_title("SysTick 系统节拍定时器：滴答时长的设置原理", fontsize=14, weight='bold', pad=10)
plt.tight_layout(); plt.savefig(f"{OUT}/fig_ppt_systick.png", dpi=190, bbox_inches='tight'); plt.close()

# ============================================================ 图B 双库初始化流程
fig, ax = plt.subplots(figsize=(11.6, 5.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 52); ax.set_axis_off()
def step(x, y, w, h, c, t1, t2='', fs=9.6):
    rbox(ax, x, y, w, h, '#FFFFFF', c, lw=1.7)
    ax.text(x+w/2, y+h/2+ (2.2 if t2 else 0), t1, ha='center', va='center', fontsize=fs, weight='bold', color=c)
    if t2: ax.text(x+w/2, y+h/2-2.4, t2, ha='center', va='center', fontsize=8.4, color=DARK)
# 公共起点
step(38, 45, 24, 6, DARK, "上电复位", "从 0x0000 0004 取 Reset_Handler")
# STD 链（左）
step(6, 36, 30, 6, BLUE, "SystemInit()", "system_stm32f4xx.c")
step(6, 27, 30, 6, BLUE, "SetSysClock()", "HSE→PLL→SW 切换")
step(6, 18, 30, 6, BLUE, "SysTick_Init(168)", "fac_us=21（HCLK÷8）")
step(6, 9, 30, 6, BLUE, "delay_ms(500)", "轮询 COUNTFLAG")
step(6, 1.2, 30, 5, BLUE, "main() while(1)", "LED 闪烁")
# HAL 链（右）
step(64, 36, 30, 6, TEAL, "HAL_Init()", "内部调 HAL_InitTick")
step(64, 27, 30, 6, TEAL, "SystemClock_Config()", "CubeMX 生成")
step(64, 18, 30, 6, TEAL, "HAL_SYSTICK_Config", "168M/1000 = 1ms 滴答")
step(64, 9, 30, 6, TEAL, "HAL_Delay(500)", "等 uwTick 增量")
step(64, 1.2, 30, 5, TEAL, "main() while(1)", "LED 闪烁")
for y0 in (45, 36, 27, 18, 9):
    arrow(ax, 21, y0, 21, y0-3, BLUE); arrow(ax, 79, y0, 79, y0-3, TEAL)
arrow(ax, 44, 45, 21, 42, BLUE); arrow(ax, 56, 45, 79, 42, TEAL)
ax.text(21, 49.2, "标准库（CH5EX01STD）", ha='center', fontsize=12, weight='bold', color=BLUE)
ax.text(79, 49.2, "HAL 库（CH5EX01HAL）", ha='center', fontsize=12, weight='bold', color=TEAL)
ax.text(50, 49.2, "", ha='center')
ax.set_title("时钟之迹 · 从上电到延时的两条代码链路", fontsize=14.5, weight='bold', pad=8)
plt.tight_layout(); plt.savefig(f"{OUT}/fig_ppt_flow.png", dpi=190, bbox_inches='tight'); plt.close()
print("PPT FIGS DONE")
