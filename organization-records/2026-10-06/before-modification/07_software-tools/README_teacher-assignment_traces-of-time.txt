STM32“时钟之迹”作业环境（已安装/已准备）
================================================

一、已安装
1. Keil MDK 5.35
   安装位置：C:\Keil_v5
   桌面快捷方式：Keil uVision5.lnk

2. STM32CubeMX 6.18.1（ST 官方包）
   文件位置：D:\Peak\Desktop\嵌入式\07_软件工具\STM32CubeMX-6.18.1
   桌面快捷方式：STM32CubeMX 6.18.1.lnk

二、已装入 Keil 的器件包
- ARM::CMSIS 5.9.0
- Keil::STM32F1xx_DFP 2.3.0（含 STM32F103VCT6）
- Keil::STM32F4xx_DFP 2.16.0（含 STM32F407ZGT6）
- Keil::STM32L4xx_DFP 2.5.0（含 STM32L496VET6）

三、老师作业现成例程
目录：D:\Peak\Desktop\嵌入式\06_例程_时钟之迹
- 5-STM32时钟系统：SYSCLK/RCC 初始化、标准外设库工程
- 7-SysTick系统定时器：SysTick、Delay 相关工程
- HAL_driver：HAL 相关源码素材
- STD_LED、STD_模板：标准库模板和示例

两个工程已经用 Keil 5.35 编译验证通过（0 Error(s), 0 Warning(s)）。

四、老师要求的 PPT 内容
- 至少 5 页正文（封面、封底不计入）
- SYSCLK 等时钟的初始化、设置和获取
- SysTick 滴答时长，以及 Delay/HAL_Delay 的调用方法
- 对上述过程画流程图（伪代码也可以）
- 总结 STM32 各时钟的原理和应用方法
- 可从 Keil MDK、STM32CubeMX 中任选其一；建议用现成 F4 工程讲解

说明：老师列出的三种芯片是“任选一种”，不需要三种都做，也不要求为了 PPT 先接实体开发板。

五、文件夹整理
- 01_安装包：MDK、CubeMX 压缩包和三种 STM32 器件包
- 02_开发库：STM32F4 标准外设库压缩包及解压目录
- 03_辅助记录：下载/验证脚本和过程截图
