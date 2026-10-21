作业2：非阻塞按键消抖代码速查

用途：在原作业“按下亮、松开灭”的 GPIO 电平控制上加入消抖。
接线：PF9 接低电平点亮的 LED；PE4 上拉输入，按键按下接地。
默认消抖 20 ms。主循环连续采样，状态稳定 20 ms 后更新；不调用延时函数。

通用模块
button_debounce.c、button_debounce.h 可直接加入项目的 User 目录，
将 .c 加入 Keil 的 User 组，User 加入头文件搜索路径。
先调用 ButtonDebounce_Init，再循环调用 ButtonDebounce_Update。
raw_pressed=1 表示按下；now_ms 使用毫秒计数。
Update 返回 PRESSED 或 RELEASED 事件，IsPressed 返回消抖后的电平状态。
uint32_t 无符号时间差处理毫秒计数回绕。

SPL 接入片段
将 spl_gpio_debounce_example.c/.h 和通用模块一起加入 User。
main.c 包含 spl_gpio_debounce_example.h，原 GPIO_Setup() 改为：
    if (SPL_ButtonLED_Init() != 0U) { while (1) {} }
原 while (1) 中的直接读写语句改为：
    SPL_ButtonLED_Poll();
stm32f4xx_it.c 包含同一头文件，在已有 SysTick_Handler 中加入：
    SPL_ButtonLED_Tick1ms();
系统时钟配置完成后调用 Init。函数从 RCC_GetClocksFreq 获取 HCLK，
SysTick_Config(HCLK / 1000) 建立 1 ms 节拍；调整时钟后重新配置时基。
HSE_VALUE 必须等于板上晶振频率，本作业工程为 8000000 Hz。

HAL 接入片段
将 hal_gpio_debounce_example.c/.h 和通用模块一起加入 User。
main.c 包含 hal_gpio_debounce_example.h，保留已有 HAL_Init() 和
SystemClock_Config()，将原 GPIO_Setup() 改为 HAL_ButtonLED_Init()。
原 while (1) 中的直接读写语句改为 HAL_ButtonLED_Poll()。
两份片段已包含 GPIO 配置，接入时移除 main.c 中原 GPIO_Setup 的声明及定义。
使用 HAL_GetTick()；保留现有 SysTick_Handler 中的 HAL_IncTick()。
HAL_RCC_ClockConfig 更新 SystemCoreClock，并重新设置 HAL 时基。
现有工程默认 1 ms 节拍，HAL 片段不定义 SysTick_Handler。

时基公式
ticks = HCLK / 1000；LOAD = ticks - 1；周期 = (LOAD + 1) / HCLK。
HCLK=168000000 Hz 时 ticks=168000，LOAD=167999，周期 1 ms。
HCLK / 100 得到 10 ms 节拍。不要将此节拍按 1 ms 累加。
消抖轮询放在主循环，循环间隔应远小于 20 ms。

验证
Arm Compiler 5.06 update 7（build 960），Cortex-M4 浮点目标。
3 个 .c 文件对象编译通过，0 错误、0 警告；本次未链接或上板运行。
build/ 下保存编译脚本、实际编译日志、build_results.json 和对象文件。
