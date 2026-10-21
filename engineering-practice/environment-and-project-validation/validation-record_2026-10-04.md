# 工程与工具验证记录（2026-10-04）

本目录 `桌面\嵌入式作业` 为本次验证的工作区；`桌面\嵌入式` 里的课程资料、例程原件均未改动。

## 一、软件环境实际核查结果

### Keil MDK（C:\Keil_v5）
| 项目 | 实际情况 |
|---|---|
| IDE 版本 | µVision V5.35.0.0（UV4.exe 文件版本 5.35.0.0） |
| 许可证 | **MDK-Lite（非商业版）**，TOOLS.INI 中 `TOOL_VARIANT=mdk_lite`，无 LIC 注册码；GUI 标题栏显示 `[Non-Commercial Use License]`，编译日志显示 `Running with Code Size Limit: 32K`（代码量限 32KB） |
| 编译器 | ARM Compiler 5.06 update 7 (build 960) 与 ARM Compiler 6.16 均已安装；本验证使用 AC5（与课程工程一致） |
| 器件包 | Keil::STM32F4xx_DFP **2.16.0**（含 STM32F407ZG，SVD 为 STM32F40x.svd）、F1xx 2.3.0、L4xx 2.5.0、ARM::CMSIS 5.8.0/5.9.0 均已安装 |
| 仿真模型 | F4 DFP 的 .pdsc 中**无外设仿真模型**，ARM\BIN 下也无 ST 器件仿真 DLL（只有内核仿真 SARMCM3 和 FVP 的 DbgFM） |

### STM32CubeMX 6.18.1（位于 桌面\嵌入式\软件工具\STM32CubeMX-6.18.1\MX）
- 本体能正常启动，固件包管理界面可联网刷新（见截图）。
- **未安装任何 STM32Cube 固件包**（含 STM32CubeF4）：默认仓库 `C:\Users\Peak\STM32Cube\Repository` 无固件包；包管理界面中 STM32F4 行 Installed Version 为空。
- 因此 **CubeMX 生成 MDK 工程的功能暂无法实际验证**（生成前必须先下载对应固件包）。
- 小问题：启动时弹一次 "Load Project" 错误框（最近工程列表里有一条失效路径），点 OK 即可，不影响使用。

### MATLAB R2025b（D:\MATLAB R2025b）
- 有许可：MATLAB、Simulink、MATLAB Coder（license('test') = 1）。
- **无许可**：Simulink Coder、Embedded Coder、Fixed-Point Designer（test = 0，产品已装但不可用）。
- **未安装任何硬件支持包**（matlabshared.supportpkg.getInstalled 返回空），即没有 STM32 支持包。
- 结论：目前可做 Simulink 建模/仿真，但不能从 Simulink 生成代码部署到 STM32（缺 Embedded Coder 许可 + STM32 支持包）。

## 二、芯片 / 板卡 / 晶振核实

- 芯片：**STM32F407ZGT6**，LQFP144。NRST 引脚号已按《DS8626_Rev12_STM32F407ZGT6数据手册.pdf》（第 50 页表 7）按列坐标核对：**LQFP144 列为第 25 脚**（LQFP100=14，LQFP176=31），与课件说法一致。
- 板卡：课程例程来自**普中 F407-T100 开发板**（例程源码注释标明"普中科技"；原理图 PDF 在 03_作业_2026-09-29 目录）。个人板卡为正点原子 F407ZGT6 板，两块板 LED 均在 PF9/PF10。
- 晶振：**HSE = 8MHz**（原理图 Y1，另见 05_分析文档\配图_F407\8MHz晶振_原理图局部.png），LSE = 32.768kHz。普中工程头文件注释"将25M修改为8M"。
- 引脚：LED0=PF9、LED1=PF10（低电平点亮）；KEY0=PE4、KEY1=PE3（按下接地）；WK_UP=PA0。
- 课件里的 **CH5EX01HAL / CH5Ex01STD 在课程平台"练习例子工程"目录（共 18 项），尚未下载**（见 05_分析文档\课程平台资源清单.md 第 98 行起）；本地用普中的时钟/SysTick 例程替代验证。

## 三、实际编译结果（全部在本工作区副本上进行，原件未动）

| 工程 | 位置 | 结果 | 产物 |
|---|---|---|---|
| 标准库工程_5-STM32时钟系统（普中） | 工程验证\01_... | **0 Error, 0 Warning**，Code=1524 | Obj\Template.axf / .hex / .map、编译日志.txt |
| 标准库工程_7-SysTick系统定时器（普中） | 工程验证\02_... | **0 Error, 0 Warning**，Code=1272 | Obj\Template.axf / .hex / .map、编译日志.txt |
| HAL最小工程（本次新建，GPIO+SysTick 1ms+168MHz） | 工程验证\03_... | **0 Error, 0 Warning**，Code=3906 | Obj\Template.axf / .hex / .map、编译日志.txt |

- 编译方式：UV4 命令行 `-b` + GUI 中 Rebuild 各一次，工具链 AC5 5.06u7，MDK-Lite（均低于 32KB 限制）。
- HAL 工程 HAL 库来源：ST 官方 GitHub 仓库 `STMicroelectronics/stm32f4xx-hal-driver`（V1.8.5，随工程存放在 HAL最小工程\STM32F4xx_HAL_Driver）；启动文件、system_stm32f4xx.c、器件头文件取自本机 F4 DFP 2.16.0；CMSIS 内核头 5.9.0。
- 过程中修复的一处配置错误：裁剪版 stm32f4xx_hal_conf.h 漏了 assert_param 宏定义，首次链接报 L6218E，补回后通过（已记录在编译日志）。

### HAL 最小工程时钟配置（按 8MHz 实际晶振计算）
HSE 8MHz → PLLM=8（VCO 输入 1MHz）→ PLLN=336（VCO 336MHz）→ PLLP=2（**SYSCLK=168MHz**）、PLLQ=7（48MHz）；AHB=/1=168MHz，APB1=/4=42MHz，APB2=/2=84MHz；Flash 等待周期 5（FLASH_LATENCY_5）；调压器 Scale 1；HSE_VALUE=8000000（工程宏定义）。SysTick 由 HAL_Init 配为 1ms 中断时基，切频后 HAL_RCC_ClockConfig 内部自动重配；HAL_Delay 基于该时基，工程内没有会重配/关闭 SysTick 的旧式延时函数。

## 四、调用链梳理（对照两套例程）

**标准库 7-SysTick 例程（上电即 168MHz）：**
startup_stm32f40_41xxx.s `Reset_Handler` → `SystemInit` → `SetSysClock`（system_stm32f4xx.c：STM32F40_41xxx 分支 PLL_M=8/N=336/P=2/Q=7，8MHz HSE → 168MHz）→ `__main` → `main` → `SysTick_Init(168)`（SysTick 时钟=HCLK/8=21MHz，fac_us=21）→ `delay_ms/delay_nms/delay_us` 轮询 SysTick->CTRL COUNTFLAG，每次等待后**关闭 SysTick**。

**标准库 5-时钟系统例程（main 里再改时钟）：**
同上 SystemInit 先到 168MHz → `main` 调 `RCC_HSE_Config(8,336,4,7)`：RCC_DeInit → HSE 开启并等待就绪 → AHB/1、APB2/2(84M)、APB1/4(42M) → PLL(PLLP=4) → 等 PLLRDY → 切换 SYSCLK 到 PLL → **实际 SYSCLK=84MHz**（例程注释自己写明"把168M的系统时钟变为84M了"）。注意：此后未调用 SystemCoreClockUpdate，`SystemCoreClock` 变量仍停留在 168000000，与实际 84MHz 不符——这正是 PPT 里"设置/获得时钟"的好例子。其延时用纯 while 空转，与时钟频率相关。

**HAL 最小工程（CubeMX 标准流程）：**
`Reset_Handler` → `SystemInit`（DFP 新版只设 FPU 和 VTOR，**不配 PLL**）→ `main` → `HAL_Init`（此时 HSI 16MHz，SysTick 按 16MHz 配 1ms）→ `SystemClock_Config`（HSE→PLL→168MHz；HAL_RCC_OscConfig/HAL_RCC_ClockConfig）→ `MX_GPIO_Init` → 主循环 HAL_GPIO_TogglePin/ReadPin/WritePin + HAL_Delay(500)（uwTick 由 SysTick_Handler→HAL_IncTick 累加）。频率获取用 `HAL_RCC_GetSysClockFreq()/GetHCLKFreq()` 系列函数，其数值来自 RCC 寄存器实读，不会过期。

## 五、仿真与烧录核实

- µVision 内核级仿真**能启动**本 HAL 工程（Debug 状态栏显示 Simulation，可加载 AXF、查看反汇编与寄存器），但运行后命令窗口立即报 **`*** error 65: access violation at 0x40023C00 : no 'read' permission`**——0x40023C00 是 Flash 接口寄存器区，说明该仿真只模拟 Cortex-M4 内核和内存，**不模拟 STM32F4 外设**（RCC/GPIO/Flash/SysTick 行为均无模型，与本节开头 DFP 无仿真模型的静态证据一致）。
- 结论：**时钟树（PLL/HSERDY）、GPIO 翻转、SysTick 计数等外设行为在本机无法仿真验证**，只能上板验证。已截图存档（截图）。
- 本机未检测到 ST-Link/J-Link/CMSIS-DAP 调试器（Get-PnpDevice 无匹配），**烧录环节不可用**；日后接板烧录前会先与你确认，避免覆盖板上程序。

## 六、补充验证（2026-10-04 下午，第二轮）

### 6.1 STM32CubeF4 固件包已装入，CubeMX 生成 MDK 工程并编译通过 ✅
- **固件包**：STM32Cube_FW_F4 **V1.28.3**（ST 官方 GitHub 发布版 tarball + 按子模块 commit b6f0ed38 补齐 HAL 驱动）已放入 CubeMX 仓库 `C:\Users\Peak\STM32Cube\Repository\STM32Cube_FW_F4_V1.28.3`，CubeMX 可正常识别使用。
  - 踩坑记录：ST 官方 GitHub 仓库把 HAL 驱动做成 git 子模块，tarball 解压后是空目录，导致第一次生成时工程里没有 HAL 源文件；已按 v1.28.3 指向的子模块 commit 补齐（100 头文件/95 源文件）。IDE 启动文件目录（Source/Templates/arm）在 GitHub 版中同样被裁剪，已从本机 F4 DFP 2.16.0 补齐。
- **生成验证**：手写 ZGT6 最小 ioc（时钟 8MHz→PLLM=8/PLLN=336/PLLP=2/PLLQ=7→168MHz，AHB/APB1/APB2=168/42/84，LED0=PF9，SWD 保留）经 CubeMX **6.18.1 命令行批处理**（`java -jar STM32CubeMX.exe -q script`，脚本 `config load / project generate`）生成 MDK-ARM V5 工程，生成器正确翻译了时钟参数（含自动算出的 FLASH_LATENCY_5）与 GPIO 配置（gpio.c 拆分模式）。
- **编译验证**：生成的 `MDK-ARM\clock168_gpio.uvprojx` 用 UV4 命令行编译 **0 Error, 0 Warning，Code=3142**（MDK-Lite 32KB 限制内）。
- 工程与日志：`CubeMX工程\clock168_gpio\`（ioc、Src/Inc、Drivers、MDK-ARM、编译日志.txt、CubeMX命令行生成日志.txt）。
- 说明：批量模式下 CubeMX 会把 .ioc 规范化重写，且对虚拟引脚有一条无害的 `VP_RIF_VS_RIF1` 提示；手动编辑 ioc 时引脚名必须按 CubeMX 命名（如 HSE 输出脚是 `PH1-OSC_OUT` 不是 `PH0-OSC_OUT`），RCC 参数必须列入 `RCC.IPParameters` 才会被采用。

### 6.4 平台资源已下载，CH5EX01 两例程编译验证通过 ✅（当晚补充）
- 借助你的 CAU VPN 会话在平台实际下载了"练习例子工程"全部 24 项（含 CH5EX01HAL/CH5Ex01STD），你手动下载的批次已由我归类，统一存放在 `../08_平台资源下载/练习例子工程/`，下载清单见该目录《下载清单.md》。
- **CH5EX01HAL（课程官方 HAL 例程）**：UV4 编译 **0 错 0 警**（Code=3390）。时钟配置：8MHz HSE → PLLM=8/N=336/P=2/Q=4 → **SYSCLK=168MHz**，FLASH_LATENCY_5、调压器 Scale 1、APB1=42M/APB2=84M。即课程 HAL 例程本身即为 168MHz 满频（PLLQ=4 使 USB 得 84MHz，非 48MHz 标准值，做 USB 时需注意）。
- **CH5Ex01STD（课程官方标准库例程）**：UV4 编译 **0 错 0 警**（Code=1528）。但模板未改时钟：STM32F40_41xxx 分支 **PLL_M=25、HSE_VALUE=25MHz**（ST 针对 25MHz 晶振探索板的默认值），本板晶振 8MHz，原样上板 SYSCLK 会错为 (8/25)×336/2≈53.76MHz，需按普中做法把 25 改 8。这与"5-时钟系统"例程中"将25修改8"的注释互相印证。
- 至此工程对照齐全：普中 2 例程 + 手写 HAL 最小工程 + CubeMX 生成工程 + 课程官方 CH5EX01HAL/CH5Ex01STD，全部可编译。

### 6.5 目录整理（当晚）
- 桌面 `嵌入式作业` 工作区已整体并入 `嵌入式/嵌入式作业/`（2089 个文件核对一致），桌面不再保留副本。
- 平台下载文件按目录归档于 `../08_平台资源下载/`（练习例子工程 24 项已齐；练习软件 8 项本机已具备无需下载；其余目录待手动下载，清单见该目录）。
- 客观题题库 docx 与本课无关，已移回桌面。

## 七、需要你决定/操作的事项（更新）

1. ~~STM32CubeF4 固件包~~ **已完成**（见 6.1）。
2. ~~CH5EX01HAL/CH5Ex01STD 例程~~ **已下载并编译验证**（见 6.4）。
3. **平台其余目录**（教师版PPT/即时交流/参考书/讲课视频/实验所用资料/潘多拉实验板）由你按需手动下载，放入 `08_平台资源下载/` 对应子文件夹。
4. **实体板 + 调试器**：时钟寄存器/PLL、SysTick 重装值（168MHz 时 LOAD=167999）、GPIO 波形的最终验证需要上板。有 ST-Link 后可安排（烧录前会先向你确认）。
5. **MATLAB**：Simulink 建模可用；如后续要走"模型→代码→STM32"流程，缺 Embedded Coder 许可和 STM32 支持包，均需学校/官方渠道解决，不在本次范围内擅自处理。

## 七、截图索引（截图\，均来自本次实际界面）
- Keil_打开HAL工程.png / Keil_HAL工程Rebuild结果.png / Keil_HAL工程编译完成.png（含 0 Error 0 Warning 与代码尺寸）
- Keil_仿真调试会话启动.png / Keil_仿真运行后停止位置.png（Simulation 状态 + error 65）
- CubeMX_主界面.png / CubeMX_Help菜单.png / CubeMX_固件包管理界面.png / CubeMX_F4固件包未安装.png
