# 平台资源下载清单（2026-10-04 晚）

来源：课程平台"课程资源"（优慕课，经 CAU VPN 访问）。本目录为下载归档区。

## 练习例子工程/（24 项，已全部到齐）

**已解压并编译验证（0 错误 0 警告，日志在本目录）：**

| 工程 | 编译结果 | 时钟结论 |
|---|---|---|
| CH5EX01HAL（HAL 库 GPIO 例程） | Code=3390 | 8MHz HSE → PLLM=8/N=336/P=2/Q=4 → **SYSCLK=168MHz**，Flash 5 等待周期，APB1=42M/APB2=84M |
| CH5Ex01STD（标准库 GPIO 例程） | Code=1528 | 模板保留 ST 官方默认：**PLL_M=25、HSE_VALUE=25MHz**（针对 25MHz 晶振的探索板）。本板晶振 8MHz，直接上板会跑错频率（(8/25)×336/2≈53.76MHz），需按普中做法把 25 改 8 |

**压缩包（未解压，按需取用）：** CHaEX01HAL.rar、CHaEx01STD.rar、CH5EX02HAL/CH5Ex02STD/CH5EX03HAL/CH5Ex03STD.rar、CH6EX01HAL/CH6EX02HAL/CH6EX03HAL/CH6Ex01STD/CH6Ex02STD.rar、CH7EX01HAL/CH7EX04STD.rar、CH8EX01HAL/CH8Ex00STD.rar、新2.rar、所附例子STD版本202308.rar、模板（基于STM32F4xx_DSP_StdPeriph_Lib_V1.8.0）.rar、！STM32F4xx_DSP_StdPeriph_Lib_V1.8.0（包括自建的工程模板）.zip

**视频/文档：** 例子视频-GPIO流水灯-标准库STD法.wmv、例子视频-GPIO流水灯-抽象库HAL法.wmv、8-配套例子题目和视频介绍二维码.pdf

## 练习软件/（8 项，未下载——本机已全部具备，可不下载）

stm32cubeide_2.2.0、ARM.CMSIS.5.9.0、Keil.STM32F4xx_DFP.2.16.0、en.stm32cubemx-win_v6-6-1、KeiMDK535、MDK注册机、Proteus8.10.SP3.Pro、STM32F4xx_DSP_StdPeriph_Lib_V1.8.0。
本机现状：MDK 5.35、CubeMX 6.18.1、F4 DFP 2.16.0、CMSIS 5.9.0 均已安装，标准库在 `07_软件工具/02_开发库/`。

## 其余目录（待手动下载，需要 CAU VPN 登录平台）

教师版PPT / 即时交流（请留意）/ 参考书（PDF格式）/ 讲课视频 / 实验所用资料 / 潘多拉实验板——内容清单见 `05_分析文档/课程平台资源清单.md`。下载后把文件放进对应同名子文件夹即可。

（客观题题库 docx 与嵌入式课程无关，已移回桌面。）
