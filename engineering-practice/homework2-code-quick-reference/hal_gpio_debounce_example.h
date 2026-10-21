#ifndef HAL_GPIO_DEBOUNCE_EXAMPLE_H
#define HAL_GPIO_DEBOUNCE_EXAMPLE_H

/* Call after HAL_Init and SystemClock_Config. Uses the existing HAL timebase. */
void HAL_ButtonLED_Init(void);
void HAL_ButtonLED_Poll(void);

#endif
