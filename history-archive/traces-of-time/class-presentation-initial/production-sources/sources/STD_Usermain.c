/**
  ******************************************************************************
  * 模板（基于STM32F4xx_DSP_StdPeriph_Lib_V1.8.0） 
  
  * 谢斌整理
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "usermain.h"

/** @addtogroup Template_Project
  * @{
  */ 

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
static __IO uint32_t uwTimingDelay;
RCC_ClocksTypeDef RCC_Clocks;

uint16_t GPIO_PIN[]={ YLED0_Pin,YLED1_Pin,YLED2_Pin,YLED3_Pin,YLED4_Pin,YLED5_Pin,YLED6_Pin,YLED7_Pin};
uint16_t Number=0,Index=0;

/* Private function prototypes -----------------------------------------------*/
static void Delay(__IO uint32_t nTime);
void LED_Init(void);


/* Private functions ---------------------------------------------------------*/

/**
  * @brief  Main program
  * @param  None
  * @retval None
  */
int main(void)
{
 
 /*!< At this stage the microcontroller clock setting is already configured, 
       this is done through SystemInit() function which is called from startup
       files before to branch to application main.
       To reconfigure the default setting of SystemInit() function, 
       refer to system_stm32f4xx.c file */

  /* SysTick end of count event each 10ms */
  RCC_GetClocksFreq(&RCC_Clocks);
  SysTick_Config(RCC_Clocks.HCLK_Frequency / 100);
  
  /* Add your application code here */
  /* Insert 50 ms delay */
  Delay(1);
	LED_Init();
  

  
     
  /* Infinite loop */
  while (1)
  {
		Delay(10);	//100ms	
		
		if(Index%5==0)
			GPIO_ToggleBits(GPIOE, LED2_Pin);//500ms	

		GPIO_SetBits(GPIOB, YLED0_Pin|YLED1_Pin|YLED2_Pin|YLED3_Pin|YLED4_Pin|YLED5_Pin|YLED6_Pin|YLED7_Pin);
		GPIO_ResetBits(GPIOB, GPIO_PIN[Number]);
		//可以考虑使用GPIO_Write(GPIOB,0xFFFF);    
		
		Index++;
		Number++;
		if(Number==8)
			Number=0;
  }
}

/**
  * @brief  Inserts a delay time.
  * @param  nTime: specifies the delay time length, in milliseconds.
  * @retval None
  */
void Delay(__IO uint32_t nTime)
{ 
  uwTimingDelay = nTime;

  while(uwTimingDelay != 0);
}

/**
  * @brief  Decrements the TimingDelay variable.
  * @param  None
  * @retval None
  */
void TimingDelay_Decrement(void)
{
  if (uwTimingDelay != 0x00)
  { 
    uwTimingDelay--;
  }
}

//LED对应IO初始化
void LED_Init(void)
{    	 
  GPIO_InitTypeDef  GPIO_InitStructure;

  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB|RCC_AHB1Periph_GPIOE, ENABLE);//使能GPIOB和E时钟

  //PE3初始化设置
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3|GPIO_Pin_4;         							//LED2对应IO口PE3
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;                  	//普通输出模式
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;                 	//推挽输出
  GPIO_InitStructure.GPIO_Speed = GPIO_High_Speed;             		//100MHz
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP;                   	//上拉
  GPIO_Init(GPIOE, &GPIO_InitStructure);                         	//初始化GPIO
	
	GPIO_SetBits(GPIOE, GPIO_Pin_3|GPIO_Pin_4);  										//高电平LED熄灭 
	
  //PB0-7初始化设置
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0|GPIO_Pin_1|GPIO_Pin_2|GPIO_Pin_3|GPIO_Pin_4|GPIO_Pin_5|GPIO_Pin_6|GPIO_Pin_7;  
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;                  
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;                 
  GPIO_InitStructure.GPIO_Speed = GPIO_High_Speed;            
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP;                   
  GPIO_Init(GPIOB, &GPIO_InitStructure);                         
	
	GPIO_SetBits(GPIOB, GPIO_Pin_0|GPIO_Pin_1|GPIO_Pin_2|GPIO_Pin_3|GPIO_Pin_4|GPIO_Pin_5|GPIO_Pin_6|GPIO_Pin_7);   
}




#ifdef  USE_FULL_ASSERT

/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t* file, uint32_t line)
{ 
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */

  /* Infinite loop */
  while (1)
  {
  }
}
#endif

/**
  * @}
  */


/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
