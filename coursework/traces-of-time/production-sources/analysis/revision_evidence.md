# 修订依据

DS8626 Rev 12，2026年3月，第106页表36：fPLL48_OUT典型48MHz、最大75MHz。HAL原例程VCO=336MHz、Q=4，计算值84MHz，超出数据手册给定范围；Q=7得到48MHz。该资料不支持“击穿”或“必然损坏”的判断。

官方来源：https://www.st.com/resource/en/datasheet/stm32f407vg.pdf

本地RM0090 Rev22，第81页表11：STM32F405/407，VDD=2.7–3.6V、150<HCLK≤168MHz，Flash LATENCY=5WS。原审校给出的表6不适用于这个修订号。

HAL原驱动stm32f4xx_hal_rcc.c中的HSE与PLL等待均使用HAL_GetTick计算超时。HAL_Init首先建立时基；HAL_RCC_ClockConfig更新SystemCoreClock并重新调用HAL_InitTick。

HAL_Delay原函数包含while((HAL_GetTick()-tickstart)<wait)循环。实现是阻塞等待；“非阻塞判定模型”不准确。基于时间差的条件判断可以用于另行编写非阻塞调度，但这不改变该函数的实际行为。

STD原主程序：uint16_t Number=0,Index=0；每轮Delay(10)，检查Index%5==0，随后Index++。使用16位无符号回卷模拟，在Index=65530开始的12轮中，翻转点为(轮0,65530)、(轮5,65535)、(轮6,0)、(轮11,5)，相邻翻转间隔为5、1、5轮；每轮名义100ms，对应500、100、500ms。

术语修订采用“时基”“节拍”“阻塞等待”“寄存器配置”“输出频率上限”等工程表述。保留课程题目“时钟之迹”。引用和真实代码保留，逐页讲解不朗读行号。
