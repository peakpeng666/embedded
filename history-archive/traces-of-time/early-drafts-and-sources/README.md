# “时钟之迹”讨论作业与例程

## 先看

- [最终演示稿 PPTX](./discussion-assignment/discussion-slides_IntelligentEquipment241_PengJunjie.pptx)：讨论帖提交文件。
- [PDF 预览](./discussion-assignment/discussion-slides_preview.pdf)：便于快速查看版面。
- [作业要求和工具环境记录](../软件工具/README_老师作业_时钟之迹.txt)。

## 例程导航

| 位置 | 内容 / 打开方式 |
|---|---|
| `工程例程/5-STM32时钟系统/` | SYSCLK、RCC 时钟配置；用 Keil 打开 `Template.uvprojx` |
| `工程例程/7-SysTick系统定时器/` | SysTick 与 Delay；用 Keil 打开 `Template.uvprojx` |
| `工程例程/STD_模板/`、`STD_LED/` | 标准库模板与 LED 示例 |
| `工程例程/HAL_driver/` | HAL 源码素材 |
| `原始压缩包/` | 老师提供的 3、4、5、7 号工程压缩包 |
| `figs/` | 演示稿配图及绘图脚本 |
| `_build/` | 演示稿生成、修复和预览导出脚本；含依赖及页面预览图 |

Keil 工程里的 `Obj/` 是编译输出；读代码时从 `User/`、`Public/` 等源码目录开始看。

## 宏开关与包含路径说明（2026-10-06 整改增补）

### 预处理宏开关

| 工程类型 | 必需宏 | 说明 |
|---|---|---|
| 标准外设库（SPL）工程 | `STM32F40_41xxx`、`USE_STDPERIPH_DRIVER` | 二者须同时定义；启动文件用 `startup_stm32f40_41xxx.s` |
| HAL 工程（教师/普中） | `USE_HAL_DRIVER`、`STM32F407xx`；普中板另需 `HSE_VALUE=8000000` | `HSE_VALUE` 必须与板上晶振一致，教师 STD 原件为 `25000000` |

### 包含路径层级

SPL 工程的典型 Include 层级：`User/`（main、it）、`Public/`（SysTick、delay）、`STM32F4xx_StdPeriph_Driver/inc`、`CMSIS/`（device 头与启动文件所在组）。HAL 工程为 `User/`、`CMSIS/`、`Drivers/STM32F4xx_HAL_Driver/Inc`。注意：Keil 工程分组与磁盘目录不一一对应（例如 HAL 工程的启动文件放在 CMSIS 组），实际构建文件以 `.uvprojx` 目标配置为准。

### 本目录现状声明

本目录当前保留 `讨论作业/`（讨论帖提交件）与 `原始压缩包/`（教师提供的 3、4、5、7 号工程压缩包原件）；`工程例程/` 未随本包存放，例程以 `原始压缩包/` 内解压原件为准。教师例程的修订版、宏配置与构建验证结果见 `../作业2与时钟之迹/代码与图件/教师例程修订与主机验证.zip` 及《作业2_重构报告》。
