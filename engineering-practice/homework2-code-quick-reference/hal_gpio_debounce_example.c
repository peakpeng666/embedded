#include "main.h"
#include "button_debounce.h"
#include "hal_gpio_debounce_example.h"

#define KEY_DEBOUNCE_MS 20U

static ButtonDebounce key;

static void GPIO_Setup(void)
{
    GPIO_InitTypeDef gpio = {0};

    __HAL_RCC_GPIOF_CLK_ENABLE();
    __HAL_RCC_GPIOE_CLK_ENABLE();

    /* PF9: active-low LED. */
    HAL_GPIO_WritePin(GPIOF, GPIO_PIN_9, GPIO_PIN_SET);
    gpio.Pin = GPIO_PIN_9;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOF, &gpio);

    /* PE4: pulled up; pressed is GPIO_PIN_RESET. */
    gpio.Pin = GPIO_PIN_4;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOE, &gpio);
}

void HAL_ButtonLED_Init(void)
{
    GPIO_Setup();
    ButtonDebounce_Init(&key, 0U, KEY_DEBOUNCE_MS, HAL_GetTick());
}

void HAL_ButtonLED_Poll(void)
{
    uint8_t raw_pressed =
        (HAL_GPIO_ReadPin(GPIOE, GPIO_PIN_4) == GPIO_PIN_RESET) ? 1U : 0U;

    (void)ButtonDebounce_Update(&key, raw_pressed, HAL_GetTick());
    HAL_GPIO_WritePin(GPIOF, GPIO_PIN_9,
                     (ButtonDebounce_IsPressed(&key) != 0U)
                         ? GPIO_PIN_RESET
                         : GPIO_PIN_SET);
}
