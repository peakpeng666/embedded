/**
  ******************************************************************************
  * @file    Project/STM32F4xx_StdPeriph_Templates/main.h 
  * @author  MCD Application Team
  * @version V1.8.0
  * @date    04-November-2016
  * @brief   Header for main.c module
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; COPYRIGHT 2016 STMicroelectronics</center></h2>
  *
  * Licensed under MCD-ST Liberty SW License Agreement V2, (the "License");
  * You may not use this file except in compliance with the License.
  * You may obtain a copy of the License at:
  *
  *        http://www.st.com/software_license_agreement_liberty_v2
  *
  * Unless required by applicable law or agreed to in writing, software 
  * distributed under the License is distributed on an "AS IS" BASIS, 
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
  *
  ******************************************************************************
  */
  
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __USERMAIN_H
#define __USERMAIN_H

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx.h"

//²¹³ä

#define LED2_Pin 					GPIO_Pin_3
#define LED2_GPIO_Port 		GPIOE
#define LED3_Pin 					GPIO_Pin_4
#define LED3_GPIO_Port 		GPIOE
#define YLED0_Pin 				GPIO_Pin_0
#define YLED0_GPIO_Port 	GPIOB
#define YLED1_Pin 				GPIO_Pin_1
#define YLED1_GPIO_Port 	GPIOB
#define YLED2_Pin 				GPIO_Pin_2
#define YLED2_GPIO_Port 	GPIOB
#define YLED3_Pin 				GPIO_Pin_3
#define YLED3_GPIO_Port 	GPIOB
#define YLED4_Pin 				GPIO_Pin_4
#define YLED4_GPIO_Port 	GPIOB
#define YLED5_Pin 				GPIO_Pin_5
#define YLED5_GPIO_Port 	GPIOB
#define YLED6_Pin 				GPIO_Pin_6
#define YLED6_GPIO_Port 	GPIOB
#define YLED7_Pin 				GPIO_Pin_7
#define YLED7_GPIO_Port 	GPIOB


/* Exported types ------------------------------------------------------------*/
/* Exported constants --------------------------------------------------------*/
/* Exported macro ------------------------------------------------------------*/
/* Exported functions ------------------------------------------------------- */
void TimingDelay_Decrement(void);

#endif /* __USERMAIN_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
