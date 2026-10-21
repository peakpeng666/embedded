# 源码与手册索引

主源目录：`D:\Peak\Desktop\嵌入式\工程实践\教师例程`。

PPT中的代码使用以下本地文件，节选只调整缩进、换行和注释，保留实际语句。

| 页 | 原文件 | 行号与用途 |
| --- | --- | --- |
| 2–5 | CH5EX01HAL/Core/Src/main.c | 73–87入口；133–155时钟设置 |
| 2、4 | CH5EX01HAL/Core/Inc/stm32f4xx_hal_conf.h | 99，HSE_VALUE=8000000 |
| 2、4 | CH5Ex01STD/UserMain/stm32f4xx.h | 143，F40_41分支HSE_VALUE=25000000 |
| 2–5 | CH5Ex01STD/UserMain/system_stm32f4xx.c | 371、384、401–403，PLL；SetSysClock函数 |
| 3 | CH5Ex01STD/STM32F4xx_Startup/startup_stm32f40xx.s | Reset_Handler调用SystemInit和__main |
| 3、6 | CH5EX01HAL/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc.c | 718–722更新HCLK软件记录和时基；Get…Freq函数 |
| 6、7、9 | CH5EX01HAL/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal.c | 256配置SysTick；312–326滴答累计和读取；389–403延时 |
| 6–8、10 | CH5Ex01STD/UserMain/Usermain.c | 20计数变量；48–53频率和滴答；60–74应用；83–100延时 |
| 7 | CH5EX01HAL/Drivers/CMSIS/Include/core_cm4.h | 2022–2036，SysTick_Config写LOAD/VAL/CTRL |
| 8 | CH5Ex01STD/UserMain/stm32f4xx_it.c | 142–145，SysTick调用TimingDelay_Decrement |
| 9 | CH5EX01HAL/Core/Src/stm32f4xx_it.c | 184–190，SysTick调用HAL_IncTick |
| 10 | CH5EX01HAL/Core/Src/main.c | 100–110，等待、翻转和流水灯移位 |
| 11 | CH5EX01HAL/Core/Src/gpio.c | 48，使能GPIOE时钟 |

标准库工程宏：`CH5Ex01STD/UserMain/CH5EX01STD.uvprojx`第340行 `STM32F40_41xxx,USE_STDPERIPH_DRIVER`。HSE和PLL计算使用该分支的定义。

官方手册：

- [ST RM0090：STM32F4参考手册](https://www.st.com/resource/en/reference_manual/rm0090-stm32f407-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)，STM32F405/407的RCC时钟树、PLL、APB定时器时钟、低速源和门控。
- [ST PM0214：Cortex-M4编程手册](https://www.st.com/resource/en/programming_manual/pm0214-stm32-cortexm4-mcus-and-mpus-programming-manual-stmicroelectronics.pdf)，SysTick系统定时器。
- [Arm Cortex-M4 Devices Generic User Guide](https://documentation-service.arm.com/static/5f2ac4ab60a93e65927bbdbf)，SysTick 24位递减计数及重装。

作业对应：SYSCLK初始化/设置/获取见3–6页；SysTick滴答设置见7页；Delay与HAL_Delay及流程见8–10页；各时钟原理与应用见5、11页。封面与结尾之外为10页正文。

修订版补充：
- P04：ST DS8626 Rev 12（2026-03），第106页表36，fPLL48_OUT最大75 MHz。官方链接：https://www.st.com/resource/en/datasheet/stm32f407vg.pdf
- P05：本地RM0090 Rev22第81页表11，2.7–3.6 V与168 MHz条件对应5 WS。
- P10：Usermain.c中uint16_t Index的65535→0回卷，详见analysis/boundary_check.py及对应JSON结果。
- P09：HAL_Delay中的while为阻塞式轮询。

2026-10-07 评审修订：

- P01：封面标签改为“HAL 时基周期 · 由 HAL_InitTick 配置”。1 ms 是 HAL_InitTick 的软件选择（stm32f4xx_hal.c:256，ticks = SystemCoreClock/1000），SysTick 外设复位后 LOAD=0 且不使能，不存在“默认周期”。
- P02：主频口径补“板上晶振差异见第 4 页”指引。
- P04：普中F407-T100开发板原理图（`课程作业/作业2/参考资料/普中F407-T100开发板原理图_STM32F407ZGT6.pdf`）晶振为 8 MHz；STD 模板 PLL_M=25 按 HSE_VALUE=25 MHz 假设（stm32f4xx.h:143），原样运行实际 SYSCLK = 8÷25×336÷2 = 53.76 MHz。
- P04：RM0090 Rev 22 第 218 页——USB OTG FS（48 MHz）、RNG（≤48 MHz）、SDIO（≤48 MHz）时钟取自 PLL48CLK；例程未启用三者，84 MHz 越限不影响运行。
- P08：实际/名义时间比 = 168 ÷ 53.76 = 3.125，标注“约 3.1 倍”。
- P09：右栏由 ①②③④ 列表重建为判断框流程图（flowChartDecision preset），对应作业第 3 问“画出流程图”；逻辑与 stm32f4xx_hal.c 389–403 一致。
