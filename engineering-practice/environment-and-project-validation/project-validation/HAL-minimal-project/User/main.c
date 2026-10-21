/**
  ******************************************************************************
  * @file    main.c
  * @brief   HAL 最小工程：GPIO 初始化与读写 + SysTick 1ms 时基 + 168MHz 时钟树。
  *
  *   时钟路径（外部晶振 8MHz）：
  *     HSE(8MHz) --/PLLM=8--> VCO 输入 1MHz --xPLLN=336--> VCO 输出 336MHz
  *       --/PLLP=2--> SYSCLK  = 168MHz
  *       --/PLLQ=7--> USB/SDIO 时钟 = 48MHz
  *     AHB  分频 1 -> HCLK  = 168MHz
  *     APB1 分频 4 -> PCLK1 = 42MHz （APB1 最高 42MHz）
  *     APB2 分频 2 -> PCLK2 = 84MHz （APB2 最高 84MHz）
  *     168MHz@3.3V 需要 5 个 Flash 等待周期（FLASH_LATENCY_5），
  *     且调压器需配置为 Scale 1（PWR_REGULATOR_VOLTAGE_SCALE1）。
  *
  *   时基说明：HAL_Init() 把 SysTick 配置为 1ms 中断（HCLK/1000 重装值），
  *   中断里调用 HAL_IncTick() 累加 uwTick；HAL_Delay() 轮询 uwTick 实现延时。
  *   整个工程只有这一套时基，不再混用标准库例程里会重配/关闭 SysTick 的
  *   轮询式 delay 函数（如 Public/SysTick.c 中的 delay_ms）。
  ******************************************************************************
  */

#include "main.h"

static void SystemClock_Config(void);
static void MX_GPIO_Init(void);

/**
  * @brief  主函数
  * @retval 无
  */
int main(void)
{
  /* 复位后 HAL 外设复位、配置 Flash 接口并初始化 SysTick 1ms 中断时基。
     此刻系统时钟仍为复位默认的 HSI 16MHz，SysTick 重装值按 16MHz 计算；
     下面 SystemClock_Config() 切到 168MHz 后，HAL_RCC_ClockConfig() 内部
     会调用 HAL_InitTick() 按新 HCLK 重新配置 SysTick。 */
  HAL_Init();

  /* 配置系统时钟为 168MHz */
  SystemClock_Config();

  /* 初始化 GPIO */
  MX_GPIO_Init();

  while (1)
  {
    /* GPIO 写操作：LED0（PF9）每 500ms 翻转一次，HAL_Delay 依赖 SysTick 1ms 时基 */
    HAL_GPIO_TogglePin(GPIOF, GPIO_PIN_9);
    HAL_Delay(500);

    /* GPIO 读操作：KEY0（PE4）按下读到低电平时点亮 LED1（PF10），松开熄灭 */
    if (HAL_GPIO_ReadPin(GPIOE, GPIO_PIN_4) == GPIO_PIN_RESET)
    {
      HAL_GPIO_WritePin(GPIOF, GPIO_PIN_10, GPIO_PIN_RESET);
    }
    else
    {
      HAL_GPIO_WritePin(GPIOF, GPIO_PIN_10, GPIO_PIN_SET);
    }
  }
}

/**
  * @brief  系统时钟配置：HSE 8MHz -> PLL -> SYSCLK 168MHz
  *         PLLM=8, PLLN=336, PLLP=2, PLLQ=7
  *         HCLK=168MHz, APB1=42MHz, APB2=84MHz
  */
static void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /* 168MHz 主频要求供电为调压器 Scale 1，先使能 PWR 时钟再配置 */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** 配置振荡器：打开 HSE，PLL 以 HSE 为输入倍频到 168MHz */
  RCC_OscInitStruct.OscillatorType      = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState            = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState        = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource       = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM            = 8;              /* VCO 输入 = 8MHz / 8   = 1MHz   */
  RCC_OscInitStruct.PLL.PLLN            = 336;            /* VCO 输出 = 1MHz  * 336 = 336MHz */
  RCC_OscInitStruct.PLL.PLLP            = RCC_PLLP_DIV2;  /* SYSCLK  = 336MHz / 2   = 168MHz */
  RCC_OscInitStruct.PLL.PLLQ            = 7;              /* USB/SDIO = 336MHz / 7  = 48MHz  */
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** 配置总线分频并切换 SYSCLK 到 PLL 输出 */
  RCC_ClkInitStruct.ClockType      = RCC_CLOCKTYPE_HCLK   | RCC_CLOCKTYPE_SYSCLK
                                   | RCC_CLOCKTYPE_PCLK1  | RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;       /* HCLK  = 168MHz */
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;         /* PCLK1 = 42MHz  */
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;         /* PCLK2 = 84MHz  */

  /* Flash 等待周期：168MHz（2.7~3.6V 供电）需要 5 个等待周期 */
  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief  GPIO 初始化：PF9/PF10 推挽输出（LED，低电平点亮），PE4 上拉输入（KEY0）
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* 使能 GPIOF（LED）与 GPIOE（按键）的 AHB1 时钟 */
  __HAL_RCC_GPIOF_CLK_ENABLE();
  __HAL_RCC_GPIOE_CLK_ENABLE();

  /* LED 引脚先写高电平，上电默认熄灭 */
  HAL_GPIO_WritePin(GPIOF, GPIO_PIN_9 | GPIO_PIN_10, GPIO_PIN_SET);

  /* LED0/LED1：PF9、PF10，推挽输出，低速 */
  GPIO_InitStruct.Pin   = GPIO_PIN_9 | GPIO_PIN_10;
  GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull  = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);

  /* KEY0：PE4，输入上拉（按键另一端接地，按下读低电平） */
  GPIO_InitStruct.Pin   = GPIO_PIN_4;
  GPIO_InitStruct.Mode  = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull  = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);
}

/**
  * @brief  出错处理：时钟或外设配置失败时停在此处，便于调试器定位
  */
void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {
  }
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  断言失败时报告出错的源文件与行号
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  (void)file;
  (void)line;
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
