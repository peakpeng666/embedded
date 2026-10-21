<!-- ppt-master-schema: design-spec/v1 -->
# 时钟之迹 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | 时钟之迹：从时钟源到一次延时 |
| Canvas Format | PPT 16:9, 1280 × 720 |
| Page Count | 12 |
| Primary Language | zh-CN |
| Target Audience | 嵌入式系统课程教师与同学 |
| Communication Intent | 用老师的真实例程讲清初始化、设置、获取、应用四阶段，覆盖作业全部要求 |
| Desired Audience Outcome | 能追踪时钟配置入口、计算总线与SysTick周期、解释两种延时函数 |
| Core Message / Ask / Action | 从时钟源经分频到节拍中断，代码中的每一步共同决定延时 |
| Delivery Context | 课堂讲解，约8分钟；页数精简 |
| Artifact Afterlife | 可编辑PPTX与逐页讲稿，课堂复习 |
| Reading Mode | balanced |
| Content Strategy | 代码取自CH5EX01HAL和CH5Ex01STD；采用简洁工程术语，补充数据手册约束与计数回卷分析，避免夸张修辞；行号集中在来源索引 |
| Design Style | 电路脉冲与技术出版排版：浅底内容、深色封面、明确语法色和大数字 |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — workflow default |
| Custom Animations | disabled — workflow default |
| Narration Audio | disabled — workflow default |
| Created Date | 2026-10-06 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 64 px |
| Content Area | 1152 × 576 px |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode Behavior**: 先给出四阶段全景，再跟随代码进入初始化、配置和读取，最后用节拍与LED串起应用；每页一个可验证结论。
- **Visual style**: custom
- **Visual Style Behavior**: 以技术出版物的网格和信号图的连线组织页面。米白内容页使用深蓝文字、青绿色关键路径与橙色差异标记，深蓝封面和结尾呼应。代码保留等宽字体和真实行号，大数字作为计算结果，连接线表达真实调用和分频关系。
- **Theme**: 沿着脉冲看代码
- **Tone**: 简洁、准确的工程表述；课堂讲解解释因果与边界，不使用夸张学术修辞。

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #F5F6F2 | 内容页背景 |
| Secondary background | #E8EEEB | 代码辅助域 |
| Primary | #132E3B | 标题、封面 |
| Accent | #167D8D | HAL、信号路径 |
| Secondary accent | #D66A35 | 标准库、差异 |
| Body text | #1D3440 | 正文 |
| Secondary text | #61747B | 页脚、出处 |
| Divider | #C9D5D2 | 边界与分隔 |
| Inverse | #F5F6F2 | 深色底文字 |
| Inverse secondary | #AABDBF | 深色底辅助文字 |
| Code accent | #73D5D4 | 深色代码的调用 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 有分量的无衬线 | Microsoft YaHei | Microsoft YaHei | sans-serif |
| Body | 清晰中文 | Microsoft YaHei | Microsoft YaHei | sans-serif |
| Code | 等宽代码 | Consolas | Consolas | monospace |
| Display | 大号等宽数字 | Consolas | Consolas | monospace |

- **Title stack**: Microsoft YaHei
- **Body stack**: Microsoft YaHei
- **Code stack**: Consolas
- **Display stack**: Consolas

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 24 |
| Title | 40 |
| Subtitle | 28 |
| Annotation | 16 |
| Code | 20 |
| Display | 68 |
| Label | 20 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 结论标题、图形或代码证据、旁注与出处。
- **Composition tendency**: 根据流程、对比、时钟分支分别使用贯穿横线、双列、非对称树状结构。
- **Cross-page continuity**: 四阶段导航；HAL青绿与STD橙色保持角色；第4、5页连续跟踪168 MHz。
- **Spacing posture**: 代码页紧凑，计算与总览页开阔。
- **Spacing anchors**: page margin 64; block gap 24; column gutter 40; corner radius 8; body leading 38.

## VI. Icon Usage Specification

- **Primary bundled library**: none

| Icon Path | Suitable Scenarios |
| --- | --- |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## IX. Content Outline

### Part 1: 沿着四个阶段追踪

#### Slide 01 - 时钟之迹
- **Audience move**: 从课题名称进入时钟到延时的具体问题。
- **Relationships**: 时钟源产生频率，SysTick以此计数，延时影响LED动作。
- **Title**: 时钟之迹
- **Core message**: 从168 MHz到一次延时，跟着真实代码走。
- **Content**: STM32F407ZGT6；Keil MDK / STM32CubeMX；CH5EX01HAL与CH5Ex01STD；初始化、设置、获取、应用。
- **Cover impact**: 168 MHz与1 ms之间的信号转换。

#### Slide 02 - 四阶段：初始化、设置、获取、应用
- **Audience move**: 从零散函数名建立四阶段定位。
- **Relationships**: 初始化先于设置；获取读取当前配置或计数；应用依赖配置与时基。
- **Title**: 四阶段：初始化、设置、获取、应用
- **Core message**: Init、Config、Get、Use分别解决入口、参数、读取和动作。
- **Content**: SystemInit/HAL_Init；SystemClock_Config/SysTick_Config；HAL_RCC_GetSysClockFreq/HAL_GetTick；Delay/HAL_Delay。原例程HAL为8 MHz、STD为25 MHz，均168 MHz。

#### Slide 03 - 初始化：启动流程与时基依赖
- **Audience move**: 能区分SystemInit、HAL_Init和SystemClock_Config的执行位置。
- **Relationships**: 复位进入SystemInit和C运行时再到main；标准库在SystemInit内部SetSysClock；HAL在main内先HAL_Init再SystemClock_Config。
- **Title**: 初始化：启动流程与时基依赖
- **Core message**: 标准库在main之前配置主频，HAL在main中配置。
- **Content**: 两条调用链；HAL_Init先在复位HSI16MHz下建立1ms时基，为HSE就绪与PLL锁定等待提供超时计数；切频后HAL_RCC_ClockConfig更新SystemCoreClock并再次HAL_InitTick；保留main原始调用顺序，讲稿不报行号。

#### Slide 04 - PLL：主频合成与输出约束
- **Audience move**: 会沿M、N、P计算主频并识别Q支路。
- **Relationships**: HSE经过M、N、P成为SYSCLK；同一个VCO经Q得到PLL48CLK。
- **Title**: PLL：主频合成与输出约束
- **Core message**: SYSCLK = HSE ÷ M × N ÷ P。
- **Content**: HAL main.c的PLL原语句；8/8×336/2=168；STD25/25×336/2=168；原HAL的Q4使PLL48输出84MHz，超过DS8626 Rev12表36给定的75MHz上限；本组参数取Q7输出48MHz。不推断击穿、损坏或实际故障。
- **Mathematical content**: 8\div8\times336\div2=168\;\mathrm{MHz}

#### Slide 05 - 总线分频与 Flash 访问时序
- **Audience move**: 能区分SYSCLK、HCLK、PCLK以及定时器时钟。
- **Relationships**: SYSCLK经AHB分频进入HCLK；HCLK分别经APB1和APB2分频；本例定时器时钟各为PCLK的2倍。
- **Title**: 总线分频与 Flash 访问时序
- **Core message**: 168 MHz主频不等于所有外设都运行在168 MHz。
- **Content**: AHB /1=168；APB1 /4=42，TIMx84；APB2 /2=84，TIMx168；APB分频1时TIM=PCLK，否则2PCLK；保留分频原代码。根据RM0090 Rev22表11，在2.7–3.6V、168MHz下配置5WS；Flash读访问时间与CPU周期不同，预取和ART缓解取指等待。

#### Slide 06 - 获取：时钟频率与累计时间
- **Audience move**: 能选择频率getter或节拍getter。
- **Relationships**: RCC getter依据配置给出Hz；HAL_GetTick依据中断累加给出ms；SystemCoreClockUpdate只更新软件记录。
- **Title**: 获取：时钟频率与累计时间
- **Core message**: Get频率读配置，GetTick读累计毫秒。
- **Content**: HAL_RCC_GetSysClockFreq根据寄存器与时钟源软件参数推算频率；GetHCLKFreq返回SystemCoreClock；GetPCLK1Freq和GetPCLK2Freq在HCLK软件记录基础上按分频计算；STD读取整组频率原调用；HAL_GetTick返回uwTick；SystemCoreClockUpdate只刷新HCLK软件记录。

#### Slide 07 - SysTick：时基周期与重装值
- **Audience move**: 会从HCLK计算LOAD与节拍周期。
- **Relationships**: SysTick24位递减计数到0触发中断并重装；HCLK源下ticks=HCLK×周期，LOAD=ticks-1。
- **Title**: SysTick：时基周期与重装值
- **Core message**: 本例HAL为1 ms，标准库为10 ms。
- **Content**: 标准库HCLK/100=1680000，LOAD1679999；HAL默认HCLK/1000=168000，LOAD167999；CMSIS SysTick_Config使用HCLK并写LOAD=ticks-1；时钟变化后重设LOAD。
- **Mathematical content**: T=(\mathrm{LOAD}+1)/f_{\mathrm{SysTick}}

#### Slide 08 - 标准库 Delay：递减计数与阻塞等待
- **Audience move**: 会把Delay的参数解释为当前节拍数。
- **Relationships**: 主循环写uwTimingDelay并等待，SysTick中断调用TimingDelay_Decrement将非零计数递减，归零返回。
- **Title**: 标准库 Delay：递减计数与阻塞等待
- **Core message**: 标准库例程Delay(10)约100 ms。
- **Content**: Usermain.c与中断文件原代码；完整循环流程；全局uwTimingDelay为__IO即volatile变量，保留对共享计数的实际访问；每10ms中断递减，Delay(10)约100ms；阻塞当前调用上下文，中断仍可执行。

#### Slide 09 - HAL_Delay：时间差判定与阻塞等待
- **Audience move**: 理解起始时间、当前时间和目标时长的比较。
- **Relationships**: SysTick中断通过HAL_IncTick累加uwTick；HAL_Delay记录起点，循环比较差值，达到wait返回。
- **Title**: HAL_Delay：时间差判定与阻塞等待
- **Core message**: HAL_Delay参数单位为毫秒。
- **Content**: HAL_Delay保留原函数；HAL_GetTick/uwTick链；wait增加一个时基周期补偿调用起点处于节拍末尾造成的欠时；HAL_Delay(1000)约1秒；while持续轮询，因此仍是阻塞式等待。区分差值算法与非阻塞调度。

#### Slide 10 - 应用：LED输出周期与计数回卷
- **Audience move**: 从原主循环推导可见动作周期。
- **Relationships**: STD每循环Delay10并判断Index模5；Index为16位无符号，65535与下一轮0均满足条件，造成相邻两轮触发；HAL每循环Delay1000并翻转LED；两次翻转构成完整亮灭周期。
- **Title**: 应用：LED输出周期与计数回卷
- **Core message**: 延时、翻转间隔与完整闪烁周期要分开。
- **Content**: 两份main实际调用节选与uint16_t声明；STD普通区间翻转500ms、完整亮灭1s、流水灯100ms；Index65535→0回卷时相邻两轮均触发，翻转间隔缩短至100ms；HAL翻转与移位约1s，亮灭周期2s；修正思路为0–4周期计数或时间差调度；精确波形用TIM/PWM。

#### Slide 11 - 时钟域分工与外设门控
- **Audience move**: 能按任务选择时钟与计时外设。
- **Relationships**: 高频源与PLL供给CPU/总线；低速源供RTC/看门狗；SysTick服务软件时基，TIM服务硬件定时。
- **Title**: 时钟域分工与外设门控
- **Core message**: 选时钟看任务，配置外设还要打开对应门控。
- **Content**: HSI16MHz内部RC，HSE外部晶振，PLL倍分频；SYSCLK/HCLK/PCLK各自作用；LSE32.768kHz与RTC，LSI约32kHz与独立看门狗；SysTick软件时基，TIM/PWM定时波形；实际GPIO时钟使能语句；启用外设前使能门控，不用时关闭以降低功耗。

#### Slide 12 - 时钟配置与软件时序的完整路径
- **Audience move**: 能沿四阶段复述并定位源码。
- **Relationships**: 初始化、设置、获取、应用形成完整追踪链；频率决定计数周期，计数周期决定延时。
- **Title**: 时钟配置与软件时序的完整路径
- **Core message**: 启动路径，再算频率，随后读状态，输出时序。
- **Content**: 四阶段回顾；STD10ms、HAL1ms，Delay与HAL_Delay均阻塞；代码出处、RM0090、PM0214与DS8626。
- **Closing impact**: 看懂一个Delay，需要把整条时钟链连起来。

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under notes/
- **Content**: 自然中文讲稿，解释实际代码、图中关系和计算步骤；源码路径与行号另留来源索引，页脚标短出处。
- **Total duration**: 约8分钟
- **Notes style**: 课堂口语，直接说明机制
- **Presentation purpose**: 用真实例程讲清四阶段和两种延时。
