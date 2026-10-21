/**
  ******************************************************************************
  * @file    stm32f4xx_hal_conf.h
  * @brief   HAL 库配置文件（最小工程裁剪版）。
  *          依据 STM32CubeF4 模板裁剪：只保留本工程用到的模块
  *          （GPIO / DMA / RCC / FLASH / PWR / CORTEX），其余模块注释掉，
  *          对应的驱动源文件也不加入工程。
  ******************************************************************************
  */

#ifndef __STM32F4xx_HAL_CONF_H
#define __STM32F4xx_HAL_CONF_H

/* ########################## 模块配置 ###############################
     本工程用到：HAL 基础模块（含 SysTick 时基）、GPIO 读写、RCC 时钟配置、
     FLASH 等待周期设置、PWR 供电配置、CORTEX（NVIC/SysTick）、DMA（RCC 关联）。
   ################################################################### */
#define HAL_MODULE_ENABLED
#define HAL_GPIO_MODULE_ENABLED
#define HAL_DMA_MODULE_ENABLED
#define HAL_RCC_MODULE_ENABLED
#define HAL_FLASH_MODULE_ENABLED
#define HAL_PWR_MODULE_ENABLED
#define HAL_CORTEX_MODULE_ENABLED

/* 其余模块（ADC/CAN/TIM/UART 等）本工程未使用，均未使能。 */

/* ########################## HSE/HSI 时钟值 #############################
     板卡外部高速晶振为 8MHz（依据《普中F407-T100开发板原理图_STM32F407ZGT6》）。
     HSE_VALUE 在 Keil 工程预定义宏中已设为 8000000，这里用条件编译兜底，
     避免重复定义。 */
#if !defined  (HSE_VALUE)
  #define HSE_VALUE    (8000000U) /*!< 外部高速晶振频率：8MHz */
#endif /* HSE_VALUE */

#if !defined  (HSE_STARTUP_TIMEOUT)
  #define HSE_STARTUP_TIMEOUT    (100U)   /*!< HSE 起振超时时间：100ms */
#endif /* HSE_STARTUP_TIMEOUT */

#if !defined  (HSI_VALUE)
  #define HSI_VALUE    (16000000U) /*!< 内部高速振荡器：16MHz */
#endif /* HSI_VALUE */

#if !defined  (LSI_VALUE)
  #define LSI_VALUE  (32000U)     /*!< 内部低速振荡器：32kHz */
#endif /* LSI_VALUE */

#if !defined  (LSE_VALUE)
  #define LSE_VALUE  (32768U)     /*!< 外部低速晶振：32.768kHz */
#endif /* LSE_VALUE */

#if !defined  (LSE_STARTUP_TIMEOUT)
  #define LSE_STARTUP_TIMEOUT    (5000U)  /*!< LSE 起振超时时间：5s */
#endif /* LSE_STARTUP_TIMEOUT */

#if !defined  (EXTERNAL_CLOCK_VALUE)
  #define EXTERNAL_CLOCK_VALUE    (12288000U) /*!< I2S 外部时钟源 */
#endif /* EXTERNAL_CLOCK_VALUE */

/* ########################### 系统配置 ######################### */
#define  VDD_VALUE                    (3300U) /*!< 供电电压 3.3V */
#define  TICK_INT_PRIORITY            (0x00U) /*!< SysTick 中断抢占优先级 0（最高） */
#define  USE_RTOS                     0U      /*!< 不使用 RTOS */
#define  PREFETCH_ENABLE              0U      /*!< F407 RevA 版本必须关闭预取，保守起见设为 0 */
#define  INSTRUCTION_CACHE_ENABLE     1U      /*!< 使能指令缓存 */
#define  DATA_CACHE_ENABLE            1U      /*!< 使能数据缓存 */

#define  USE_HAL_GPIO_REGISTER_CALLBACKS      0U
#define  USE_HAL_DMA_REGISTER_CALLBACKS       0U
#define  USE_HAL_RCC_REGISTER_CALLBACKS       0U
#define  USE_HAL_FLASH_REGISTER_CALLBACKS     0U
#define  USE_HAL_PWR_REGISTER_CALLBACKS       0U
#define  USE_HAL_CORTEX_REGISTER_CALLBACKS    0U

/* ########################## 断言选择 ############################## */
/* #define USE_FULL_ASSERT    1U */

#ifdef  USE_FULL_ASSERT
/**
  * @brief  参数检查宏：开启 USE_FULL_ASSERT 后，断言失败会调用 assert_failed()
  */
  #define assert_param(expr) ((expr) ? (void)0U : assert_failed((uint8_t *)__FILE__, __LINE__))
  void assert_failed(uint8_t *file, uint32_t line);
#else
  #define assert_param(expr) ((void)0U)
#endif /* USE_FULL_ASSERT */

/* 包含已使能模块的头文件 */
#ifdef HAL_RCC_MODULE_ENABLED
  #include "stm32f4xx_hal_rcc.h"
#endif /* HAL_RCC_MODULE_ENABLED */

#ifdef HAL_GPIO_MODULE_ENABLED
  #include "stm32f4xx_hal_gpio.h"
#endif /* HAL_GPIO_MODULE_ENABLED */

#ifdef HAL_DMA_MODULE_ENABLED
  #include "stm32f4xx_hal_dma.h"
#endif /* HAL_DMA_MODULE_ENABLED */

#ifdef HAL_FLASH_MODULE_ENABLED
  #include "stm32f4xx_hal_flash.h"
#endif /* HAL_FLASH_MODULE_ENABLED */

#ifdef HAL_PWR_MODULE_ENABLED
  #include "stm32f4xx_hal_pwr.h"
#endif /* HAL_PWR_MODULE_ENABLED */

#ifdef HAL_CORTEX_MODULE_ENABLED
  #include "stm32f4xx_hal_cortex.h"
#endif /* HAL_CORTEX_MODULE_ENABLED */

/* 注意：USE_HAL_DRIVER、STM32F407xx、HSE_VALUE 均在 Keil 工程
   Options -> C/C++ -> Preprocessor Symbols 中定义，不在此处重复。 */

#endif /* __STM32F4xx_HAL_CONF_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
