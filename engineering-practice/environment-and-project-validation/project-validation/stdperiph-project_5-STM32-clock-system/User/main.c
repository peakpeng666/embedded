/*******************************************************************************
*                 
*                 		       普中科技
--------------------------------------------------------------------------------
* 实 验 名		 : STM32时钟系统
* 实验说明       : 
* 连接方式       : 
* 注    意		 : LED驱动文件在led.c内
*******************************************************************************/

#include "stm32f4xx.h"
#include "led.h"

/*******************************************************************************
* 函 数 名         : delay
* 函数功能		   : 延时函数，通过while循环占用CPU，达到延时功能
* 输    入         : i
* 输    出         : 无
*******************************************************************************/
void delay(u32 i)
{
	while(i--);
}

/*******************************************************************************
* 函 数 名         : RCC_HSE_Config
* 函数功能		   : 自定义系统时钟
* 输    入         : pllm：VCO 输入时钟 分频因子，范围0-63
					 plln：VCO 输出时钟 倍频因子，范围192-432
					 pllp：PLLCLK 时钟分频因子，范围2, 4, 6, or 8
					 pllq：OTG FS,SDIO,RNG 时钟分频因子，范围4-15
* 输    出         : 无
*******************************************************************************/
void RCC_HSE_Config(u32 pllm,u32 plln,u32 pllp,u32 pllq)
{
	RCC_DeInit(); //将外设RCC寄存器重设为缺省值
	RCC_HSEConfig(RCC_HSE_ON);//设置外部高速晶振（HSE）
	if(RCC_WaitForHSEStartUp()==SUCCESS) //等待HSE起振
	{
		RCC_HCLKConfig(RCC_SYSCLK_Div1);//设置AHB时钟（HCLK）
		RCC_PCLK2Config(RCC_HCLK_Div2);//设置低速APB2时钟（PCLK2）
		RCC_PCLK1Config(RCC_HCLK_Div4);//设置低速APB1时钟（PCLK1）
		RCC_PLLConfig(RCC_PLLSource_HSE,pllm,plln,pllp,pllq);//设置PLL时钟源及倍频系数
		RCC_PLLCmd(ENABLE); //使能或者失能PLL
		while(RCC_GetFlagStatus(RCC_FLAG_PLLRDY)==RESET);//检查指定的RCC标志位设置与否,PLL就绪
		RCC_SYSCLKConfig(RCC_SYSCLKSource_PLLCLK);//设置系统时钟（SYSCLK）
		while(RCC_GetSYSCLKSource()!=0x08);//返回用作系统时钟的时钟源,0x08：PLL作为系统时钟
	}	
}

/*******************************************************************************
* 函 数 名         : main
* 函数功能		   : 主函数
* 输    入         : 无
* 输    出         : 无
*******************************************************************************/
int main()
{
	RCC_HSE_Config(8,336,4,7); //将pllp=2修改为4，相当于把168M的系统时钟变为84M了
	LED_Init();
	while(1)
	{
		GPIO_ResetBits(GPIOF,GPIO_Pin_9);//复位F9
		delay(6000000);
		GPIO_SetBits(GPIOF,GPIO_Pin_9);//置位F9
		delay(6000000);
	}
}


