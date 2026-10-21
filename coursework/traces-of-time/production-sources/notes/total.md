# 01_cover

本次讨论以STM32F407为例，沿初始化、设置、获取、应用四个阶段分析时钟配置与软件延时。代码来自老师提供的CH5EX01HAL和CH5Ex01STD。重点是三层关系：PLL如何产生168 MHz系统时钟，总线与SysTick如何分配和计数，以及两种延时函数如何决定LED输出时序。封面右侧的 1 ms 指 HAL 时基周期，由 HAL_InitTick 配置 SysTick 产生；SysTick 外设复位后不运行，1 ms 是软件的选择。

---

# 02_four_stages

初始化阶段建立复位后的运行环境，关注SystemInit与HAL_Init。设置阶段配置PLL、总线分频和SysTick周期。获取阶段分别读取时钟频率和累计毫秒数。应用阶段则利用这些计数执行延时和安排任务时序。两份工程的HSE参数不同：HAL按板上的8 MHz晶振配置，标准库模板按25 MHz晶振假设配置，经过各自的PLL参数后，都按168 MHz设计；标准库在8 MHz晶振板上原样运行的实际主频只有53.76 MHz，第4页展开。后面按这四个阶段对照实际代码。

---

# 03_init

启动文件先调用SystemInit，再进入C运行时初始化，最后执行main。标准库在SystemInit内调用SetSysClock，因此进入main前已完成主时钟配置。HAL工程在main中依次调用HAL_Init、SystemClock_Config和MX_GPIO_Init。这个顺序有明确依赖：HAL_Init先在复位后的HSI 16 MHz下建立1 ms时基，后续HSE就绪检测、PLL锁定等待中的超时判断都使用HAL_GetTick。切换到168 MHz后，HAL_RCC_ClockConfig更新SystemCoreClock，并再次调用HAL_InitTick，使时基继续保持1 ms。

---

# 04_pll

HAL工程以8 MHz HSE为输入，除以M等于8，得到1 MHz；乘以N等于336，得到336 MHz VCO；再除以P等于2，得到168 MHz系统时钟。标准库使用25 MHz输入与M等于25，计算结果相同。Q控制另一条输出：原HAL代码Q等于4，得到84 MHz。DS8626 Rev 12表36规定PLL48输出最大为75 MHz，因此该参数组合超出数据手册给定范围。对于这里336 MHz的VCO，取Q等于7即可得到48 MHz，也满足USB全速时钟频率要求。标准库原例程的Q值就是7。标准库的主频假设还要单独看：模板把PLL_M写成25，对应25 MHz晶振；普中T100板的晶振是8 MHz，原样运行时实际SYSCLK为8除以25乘336除2，即53.76 MHz，SystemCoreClock仍按168 MHz报告，需要把M改成8。84 MHz只涉及PLL48CK：参考手册规定该输出来自PLL48CLK，服务USB OTG FS、SDIO和RNG，本例程都未启用，所以越限不构成功能问题，配置仍应按数据手册取Q等于7。

---

# 05_clock_tree

168 MHz系统时钟经AHB除以1，HCLK仍为168 MHz；APB1除以4得到42 MHz，APB2除以2得到84 MHz。F407的定时器时钟需要单独计算：APB分频等于1时，TIM时钟等于PCLK；分频大于1时，TIM时钟等于2倍PCLK。因此本例APB1定时器为84 MHz，APB2定时器为168 MHz。Flash访问也受频率与供电电压约束。RM0090 Rev22表11规定，在2.7至3.6 V、168 MHz条件下，应配置5个等待周期。Flash读取时间与CPU周期不同，等待周期保证访问时序，预取和ART加速器用于减轻取指等待。

---

# 06_get

获取函数读取的对象不同。HAL_RCC_GetSysClockFreq根据RCC寄存器和HSE_VALUE等时钟源参数计算SYSCLK。HAL_RCC_GetHCLKFreq直接返回软件变量SystemCoreClock；PCLK获取函数再按APB分频计算频率。SystemCoreClockUpdate只刷新这份HCLK记录，不会重新配置硬件时钟。标准库通过RCC_GetClocksFreq获得一组频率数据。HAL_GetTick读取的则是中断维护的uwTick，单位为毫秒。频率计算结果与累计时间属于不同的数据，使用时应区分。

---

# 07_systick

SysTick是24位递减计数器，计数到零产生事件，随后自动重装。周期满足T等于LOAD加1，再除以SysTick计数时钟频率。两份例程调用的CMSIS函数均选择HCLK。标准库将168 MHz除以100，形成10 ms时基，LOAD为1679999。HAL默认将168 MHz除以1000，形成1 ms时基，LOAD为167999。HAL表达式中的uwTickFreq默认值为1。更改HCLK后，必须相应更新重装值，才能维持原定时基周期。

---

# 08_delay

标准库Delay采用递减计数。主程序先将参数写入uwTimingDelay，再循环检查它是否为零。SysTick每10 ms进入中断，通过TimingDelay_Decrement将非零计数减1；归零后Delay返回。原文件中的共享变量使用__IO，也就是volatile限定，要求编译器保留对这个对象的实际访问，使主程序能够观察到中断对计数的修改。Delay阻塞主程序的后续执行，但中断仍可执行。这里一个参数单位对应10 ms，所以Delay(10)约为100 ms，Delay(1)约为10 ms。以上时间都按SystemCoreClock等于168 MHz计算；标准库模板假设25 MHz晶振，板上焊接8 MHz晶振时实际主频53.76 MHz，列出时间均变为约3.1倍。

---

# 09_hal_delay

HAL_Delay采用累计时间差判断。函数先读取HAL_GetTick记录起点，再将请求时长保存为wait。它额外增加一个时基周期，是为了补偿调用起点接近当前节拍末尾时可能出现的欠时等待。随后while循环不断比较当前计数减去起点的结果，达到wait后才返回。所以这个函数仍是阻塞式等待，差值算法本身不意味着非阻塞。时基配置、累计、读取、使用，分别对应HAL_InitTick、HAL_IncTick、HAL_GetTick和HAL_Delay。原main中的HAL_Delay(1000)约等待1 s。右侧流程图概括全过程：进入函数先读tickstart并算出wait，再循环比较经过时间与wait，未达到继续轮询，达到后返回主循环；轮询期间的节拍来自SysTick中断中的HAL_IncTick，周期由HAL_InitTick配置为1 ms。若要使用非阻塞调度，应把时间差判断放回主循环，在尚未到期时继续处理其他工作。

---

# 10_application

标准库每轮Delay(10)，流水灯约每100 ms移位。Index对5取模为零时翻转LED，因此普通区间内翻转间隔约500 ms，完整亮灭周期约1 s。这里还有一个边界：Index是16位无符号变量。65535对5取模为零，执行一次翻转；随后Index递增回卷到0，下一轮条件又成立。因此回卷前后两次翻转只间隔一轮，也就是约100 ms。改为0到4的周期计数，或直接依据经过时间判断，可以保持一致的触发间隔。HAL例程每轮等待约1 s并翻转一次，完整亮灭周期约2 s。精确周期波形可以交给TIM或PWM。

---

# 11_clock_roles

高速时钟部分，HSI是内部16 MHz RC，HSE提供外部晶振参考，PLL负责频率合成。系统选择出的SYSCLK经AHB、APB分频，形成CPU、总线和外设各自的时钟。低速部分，外部32.768 kHz的LSE适合RTC走时，内部约32 kHz的LSI供独立看门狗等使用。SysTick主要提供软件时基，TIM和PWM用于周期中断与定时波形。外设时钟还需要门控使能，页面底部是原GPIO初始化文件中使能GPIOE的语句。未使用的外设可以关闭时钟，减少动态功耗。

---

# 12_close

四个阶段构成完整的分析路径：初始化确认启动顺序，设置阶段确定主频、总线与时基周期，获取阶段区分寄存器计算结果、软件频率记录和累计时间，应用阶段再分析等待条件与输出时序。这两份例程的SysTick周期分别为10 ms和1 ms，两种延时函数都采用阻塞等待。把时钟树、计数方式与主循环条件结合起来，就能解释正常输出周期，也能定位参数越界和计数回卷造成的变化。
