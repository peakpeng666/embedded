# 潘多拉：EDA 图纸与硬件核对

主交付是 `lceda/Pandora_L496_lceda-export.json`，嘉立创 EDA 标准版导出的四页原生工程。元器件、100 脚 MCU、导线、网络标签、流程框和箭头均可编辑。

打印版：`../../verified-drawings/Verified_four-page-bound-volume.pdf`，四页 A3 横向。分页 PDF、PNG 和可编辑源文件在同目录。

## 文件

| 文件 | 内容 |
| --- | --- |
| `lceda/Pandora_L496_lceda-export.json` | 嘉立创实际导出的原生工程，编辑入口 |
| `lceda/Pandora_L496_lceda-saved.json` | 应用首次保存的副本 |
| `lceda/Pandora_L496_schematic-and-flowcharts.json` | 生成器输入版本 |
| `lceda/Pandora_L496_lceda-export.net` | Protel/Altium 网表 |
| `lceda/lceda-original-export.pdf` | 嘉立创直接导出的四页 PDF |
| `lceda/01_lceda-export.svg` … `04_lceda-export.svg` | 四页矢量图 |
| `lceda/verification-results.json` | 网表、引脚与哈希核对结果 |
| `verified-images/` | 四页最终 PNG |
| `official_sources.json` | 官方资料下载页、文件名与 SHA-256 |

打开方式：嘉立创 EDA 标准版中选择“文件 → 打开 → 嘉立创EDA”，导入 `Pandora_L496_lceda-export.json`。使用工程离线模式即可保存到本地。

## 核对结果

- 嘉立创导出的 25 个网络逐项比较了完整成员集合，39 个器件核对了标值。
- U3 的 100 个引脚名、引脚号与 ST CubeMX 的 LQFP100 XML 一致。
- J1 实际连接为 `UART1_TX = U3-68 / J1-4 / J1-1`，`UART1_RX = U3-69 / J1-3 / J1-2`。
- 四页 PDF 已逐页渲染检查。结果在 `lceda/verification-results.json`，判断依据在 [`critical_review.md`](./critical_review.md)。

## 官方资料

资料来自[正点原子官方下载中心](http://www.openedv.com/docs/boards/iot/zdyz_panduola.html)的“新资料”：原理图包、入门资料和《潘多拉 STM32L4 开发指南 V1.1》。

- [夸克网盘](https://pan.quark.cn/s/65fa193e56a3)，提取码 `dhFn`。
- [百度网盘](https://pan.baidu.com/s/17T9ZlkHhXO7ZF1ixRkGCEQ)，提取码 `mznq`。

原始资料保存在 `hardware/sources/`（本地）：V3.4 原理图、元器件位置图、IO 分配表、V2.4 历史图、入门说明和 319 页开发指南。

## 型号与版本

官方指南第 18、23、27 页写明 MCU 为 STM32L496VET6、LQFP100、320 KB SRAM、512 KB Flash。V3.4 电路包含 DAP/USB_UART、Type-C USB、PD10/KEY0、PD9/KEY1、PE7/8/9 RGB 和 PA9/10 USART1，与实板接口一致。

原图 U3 的器件文字仍写 STM32L475VET6；摘编版保留原字样，原生 EDA 图按官方指南和当前工程写 STM32L496VET6。两版均标注这一差异。

VREF 旁注写 R18，图中对应器件是 R13 / 10R，重绘按器件标注。C28 为 100 nF，C29 为 2.2 µF。R13 的阻值未在实物上测量。

引脚核对使用 [ST DS11585 Rev20](https://www.st.com/resource/en/datasheet/stm32l496ve.pdf) 第 68 页。

## 重新生成

以下命令从 `engineering-practice/embedded` 工程目录执行。干净克隆可直接阅读已提交的原生工程和打印成品；完整重生成不是仅靠 Git 文件即可完成：

- `create_official_schematics.py`、`create_lceda_project.py`、`verify_lceda_export.py` 需要本地 `hardware/sources/` 原厂 PDF 与 `STM32L496VETx_ST_CubeMX_pins.xml`。请按 `official_sources.json` 核实来源/哈希，先补齐输入。
- `prepare_lceda_print.py` 使用已提交的 `hardware/lceda/lceda-original-export.pdf`；脚本会创建 `output/pdf/`。
- `export_verified_folder.py` 使用相邻 `../verified-drawings/` 内现有原生工程、PDF 和网表，会创建 `logs/` 与 `output/pdf/`。
- `package_delivery.py` 还需要已生成的两份 PDF、本地 Windows 前后验收日志和相邻 `../keil-board-demos/` 录像/字幕。缺失时会在复制任何交付内容之前列出缺失项并停止。不得用虚构日志替代实板证据。

主机单元测试可离线运行，但不等同于板卡、Keil、CubeIDE 或图纸复测。旧 v1.0.0 交接包应独立解压，不能覆盖新工程来补输入。

```powershell
.\.venv\Scripts\python.exe hardware\create_official_schematics.py
C:\Python312\python.exe hardware\create_lceda_project.py
# 在嘉立创中导入新 JSON，重新保存并导出网表和 PDF
C:\Python312\python.exe hardware\verify_lceda_export.py
.\.venv\Scripts\python.exe hardware\prepare_lceda_print.py
```

摘编与打印转换需要 ReportLab、PyMuPDF 和 Windows 字体；原生 JSON 生成只需要 Python 标准库。

