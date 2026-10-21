/**
  ******************************************************************************
  * @file    main.h
  * @brief   HAL 最小工程头文件：引脚分配与时钟参数说明。
  *
  *   芯片：STM32F407ZGT6（LQFP144 封装，NRST 为第 25 脚）
  *   板卡：普中 F407-T100 开发板（原理图：《普中F407-T100开发板原理图_STM32F407ZGT6》）
  *   引脚：LED0 = PF9、LED1 = PF10（低电平点亮）；KEY0 = PE4（按下为低电平）
  *   晶振：外部高速晶振 HSE = 8MHz，外部低速晶振 LSE = 32.768kHz
  ******************************************************************************
  */

#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

#include "stm32f4xx_hal.h"

/* 出错处理函数（main.c 中定义） */
void Error_Handler(void);

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
