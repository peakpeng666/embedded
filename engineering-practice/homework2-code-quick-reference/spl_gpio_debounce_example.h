#ifndef SPL_GPIO_DEBOUNCE_EXAMPLE_H
#define SPL_GPIO_DEBOUNCE_EXAMPLE_H

#include <stdint.h>

/* Call after system clocks are configured. Returns 0 on success. */
uint32_t SPL_ButtonLED_Init(void);
void SPL_ButtonLED_Poll(void);

/* Call once per interrupt from the existing 1 ms SysTick_Handler. */
void SPL_ButtonLED_Tick1ms(void);

#endif
