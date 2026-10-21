#include "stm32f4xx.h"
#include "button_debounce.h"
#include "spl_gpio_debounce_example.h"

#define KEY_DEBOUNCE_MS 20U

static volatile uint32_t now_ms;
static ButtonDebounce key;

static void GPIO_Setup(void)
{
    GPIO_InitTypeDef gpio;

    RCC_AHB1PeriphClockCmd(
        RCC_AHB1Periph_GPIOF | RCC_AHB1Periph_GPIOE, ENABLE);

    /* PF9: active-low LED. Set the output latch before switching to output. */
    GPIO_SetBits(GPIOF, GPIO_Pin_9);
    GPIO_StructInit(&gpio);
    gpio.GPIO_Pin = GPIO_Pin_9;
    gpio.GPIO_Mode = GPIO_Mode_OUT;
    gpio.GPIO_OType = GPIO_OType_PP;
    gpio.GPIO_Speed = GPIO_Speed_2MHz;
    gpio.GPIO_PuPd = GPIO_PuPd_NOPULL;
    GPIO_Init(GPIOF, &gpio);

    /* PE4: pulled up; the switch connects the pin to ground when pressed. */
    gpio.GPIO_Pin = GPIO_Pin_4;
    gpio.GPIO_Mode = GPIO_Mode_IN;
    gpio.GPIO_PuPd = GPIO_PuPd_UP;
    GPIO_Init(GPIOE, &gpio);
}

uint32_t SPL_ButtonLED_Init(void)
{
    RCC_ClocksTypeDef clocks;

    GPIO_Setup();
    now_ms = 0U;
    ButtonDebounce_Init(&key, 0U, KEY_DEBOUNCE_MS, now_ms);
    RCC_GetClocksFreq(&clocks);

    /* SysTick uses HCLK. The CMSIS function writes LOAD = ticks - 1. */
    return SysTick_Config(clocks.HCLK_Frequency / 1000U);
}

void SPL_ButtonLED_Tick1ms(void)
{
    ++now_ms;
}

void SPL_ButtonLED_Poll(void)
{
    uint8_t raw_pressed =
        (GPIO_ReadInputDataBit(GPIOE, GPIO_Pin_4) == Bit_RESET) ? 1U : 0U;

    (void)ButtonDebounce_Update(&key, raw_pressed, now_ms);
    if (ButtonDebounce_IsPressed(&key) != 0U)
    {
        GPIO_ResetBits(GPIOF, GPIO_Pin_9);
    }
    else
    {
        GPIO_SetBits(GPIOF, GPIO_Pin_9);
    }
}
