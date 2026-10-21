# 潘多拉：专业 EDA 图纸、官方依据与实际实现核对

主交付是 `lceda/Pandora_L496_嘉立创导出.json`，为**嘉立创 EDA 标准版实际导出的原生四页工程**。元器件、100 脚 MCU、导线、网络标签、流程框和箭头均可编辑。已经在本机嘉立创 EDA 6.5.51 中导入、保存，导出原生 JSON、PDF 和 Protel/Altium 网表，再检查实际导出结果。不是给图片改扩展名。

打印版：`../output/pdf/潘多拉_嘉立创EDA_原理图与流程图.pdf`，四页 A3 横向，分别是最小系统、实验电路、主循环与中断流程、消抖与 RGB 状态机。文字转换为矢量轮廓，避免换电脑缺字体；编辑时使用原生 JSON。

本机软件启动路径：`D:\Embedded\Tools\LCEDA\app\lceda.exe`。在**文件 → 打开 → 嘉立创EDA**中选择上述 JSON，再点击“导入”。使用“工程离线模式”，可保存到本地，不要求登录。最终导出的项目名为 `Pandora_L496_Verified`。`Pandora_L496_原理图与流程图.json` 保留生成器的输入版本，`Pandora_L496_嘉立创保存.json` 保留应用最初的保存副本。

## 已完成的独立核对

- 对嘉立创实际导出的 `lceda/Pandora_L496_嘉立创导出.net` 检查了 **25 个网络的全部成员、39 个器件的标值**，而不是只检查生成器内部坐标。
- U3 原生符号和嘉立创保存副本的 **100 个引脚名、引脚号**，均与 ST CubeMX 的 LQFP100 XML 一一比对通过。
- J1 的网络实际包含 `UART1_TX = U3-68 / J1-4 / J1-1`，`UART1_RX = U3-69 / J1-3 / J1-2`；没有误按常见排针顺序连接 1–2、3–4。
- 四页 PDF 逐页渲染检查。结果在 `lceda/核对结果.json`；详细判断和代码依据在 `critical_review.md`。

这些检查仅覆盖本次摘绘范围。没有为未展开的 GPIO 标注“实板未连接”，也没有指定未经核实的 PCB 封装，不能据此直接投板。

本次从[正点原子官方下载中心](http://www.openedv.com/docs/boards/iot/zdyz_panduola.html)进入其资料盘，下载“新资料”中的原理图包、入门资料和《潘多拉 STM32L4 开发指南 V1.1》。不是把其它 L496 开发板的图当成潘多拉图。

资料盘入口：

- [夸克网盘](https://pan.quark.cn/s/65fa193e56a3)，提取码 `dhFn`。
- [百度网盘](https://pan.baidu.com/s/17T9ZlkHhXO7ZF1ixRkGCEQ)，提取码 `mznq`。
- 目录：`【正点原子】潘多拉IoT开发板 / 【正点原子】潘多拉IoT开发板资料（新资料）`。

本地完整资料在 `hardware/sources/`，其中 `ALIENTEK_Pandora_official/` 保存厂商原始 V3.4 原理图、元器件位置图、IO 分配表、V2.4 历史图和入门说明；`ALIENTEK_Pandora_STM32L4_Manual_V1.1.pdf` 为完整 319 页开发指南。

## 型号与版本核对

官方指南 PDF 第 18、23、27 页明确 MCU 为 **STM32L496VET6、LQFP100、320 KB SRAM、512 KB Flash**；第 52 页按 L496 创建 Keil 工程，第 65 页使用 `STM32L496xx` 宏。与本次工程及读到的 Flash 容量相符。

官方 V3.4 电路包含 **DAP&USB_UART、Type-C USB、PD10/KEY0、PD9/KEY1、PE7/8/9 RGB 和 PA9/10 USART1**，与本次使用的接口特征匹配。原图 U3 的器件文字仍为 `STM32L475VET6`：官方图摘编版保留原字样；原生 EDA 重绘版依官方开发指南及当前工程写 `STM32L496VET6`，两版都注明此差异。SWD 的器件族 ID 与 Flash 容量不能单独鉴定完整芯片料号；本次未用相机读取芯片顶标。PCB 丝印版本也不能从现有 USB/SWD 信息直接读出，因此 V3.4 是目前接口特征最匹配的厂商图，不据此声称已读出实物 PCB 版本。

J2 是 DAP 控制器自身的调试接口；目标 MCU 的网络是 `T_JTMS / T_JTCK / RESET`。日常连接使用板上的 USB_COM。本次没有改写 DAP 固件或 MCU 选项字节。

## 官方图摘编参考版

`output/pdf/STM32L496_最小系统与实验电路_官方图版.pdf` 为两页 A3 横向矢量图：

1. 主控最小系统、电源去耦、时钟、BOOT、复位与 VREF+，附 L496/LQFP100 引脚对照。
2. 共阳 RGB、低有效按键、DAP、USART1 跳线和 Type-C USB 电路，附本次固件的网络映射。

同目录提供 PNG 和 SVG。图中的线路、符号、器件值直接取自厂商 PDF；文字转为矢量轮廓以避免原图未嵌入字体导致的跨电脑显示差异。配套的标题与引脚对照是新增整理说明。原始厂商文件未修改。

此摘编版用于对照来源。满足专业软件可编辑要求的主交付是上面的嘉立创原生工程。

两处原厂资料冲突已经记录：VREF 旁注写 R18，而图中的对应器件明确是 **R13 / 10R**，重绘按器件标注；原图 U3 写 L475，配套官方指南写 L496。R13 未在实板上测量，不能把图中标值说成实测值。C28 为 100 nF，C29 为 2.2 µF；没有互换。

核对 L496 引脚时使用了 [ST DS11585 Rev20](https://www.st.com/resource/en/datasheet/stm32l496ve.pdf) 第 68 页。下载来源、型号差异、文件 SHA-256 见 `official_sources.json`。

重新生成和核对：

```powershell
.\.venv\Scripts\python.exe hardware\create_official_schematics.py
C:\Python312\python.exe hardware\create_lceda_project.py
# 在嘉立创中导入新 JSON，重新保存并导出网表和 PDF；不要用旧导出物核对新工程。
C:\Python312\python.exe hardware\verify_lceda_export.py
.\.venv\Scripts\python.exe hardware\prepare_lceda_print.py
```

摘编与打印转换需要 ReportLab、PyMuPDF 和 Windows 字体；原生 JSON 生成只需要 Python 标准库。打印转换读取嘉立创实际导出的 PDF，仅转文字轮廓与 A3 页面，不重画电路。
