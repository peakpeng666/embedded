# 作业 3

- [PDF 成品](./homework3_IntelligentEquipment241_PengJunjie_2024306100324.pdf)
- [LaTeX 源文件](./homework3_IntelligentEquipment241_PengJunjie_2024306100324.tex)
- [编译脚本](./build-pdf.ps1)

共 3 页，保留题目原文，使用宋体正文、黑体标题，与作业 2 的格式一致。

第 1 页：GPIOD_BASE 的计算、各端口基址与 OTYPER 的地址。第 2 页：输入、输出所需寄存器及工作过程。第 3 页：位结构图上的流向标注、BSRR 的用法与 IDR/ODR 的区别。

| 目录 | 内容 |
| --- | --- |
| [latex_assets](./latex_assets/) | GPIO 位结构图；箭头和寄存器标注由 LaTeX/TikZ 绘制 |

GPIOD_BASE = 0x4002 0C00，OTYPER 的偏移为 0x04，所以地址是 0x4002 0C04。在 C 表达式中，`&GPIOD->OTYPER` 取地址，`GPIOD->OTYPER` 访问寄存器内容。

先通过 RCC_AHB1ENR 使能端口时钟。输入模式配置 MODER、PUPDR，读 IDR；输出模式配置 MODER、OTYPER、OSPEEDR，并按电路需要选择 PUPDR，写 ODR 或 BSRR。表中值针对单个引脚的位字段。

在本目录运行编译PDF.ps1，或用 XeLaTeX 编译源文件两次。需要安装宋体（SimSun）、黑体（SimHei）、Times New Roman、Consolas 和 Segoe UI Symbol。脚本在 `_build/latex` 中编译，并将 PDF 更新到本目录。
