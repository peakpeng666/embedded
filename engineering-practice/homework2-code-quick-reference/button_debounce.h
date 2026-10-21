#ifndef BUTTON_DEBOUNCE_H
#define BUTTON_DEBOUNCE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum
{
    BUTTON_EVENT_NONE = 0,
    BUTTON_EVENT_PRESSED,
    BUTTON_EVENT_RELEASED
} ButtonEvent;

typedef struct
{
    uint32_t changed_at_ms;
    uint32_t debounce_ms;
    uint8_t stable_pressed;
    uint8_t candidate_pressed;
} ButtonDebounce;

/* Call once. initial_pressed and raw_pressed use 1 for pressed, 0 for released. */
void ButtonDebounce_Init(ButtonDebounce *button, uint8_t initial_pressed,
                         uint32_t debounce_ms, uint32_t now_ms);

/* Call repeatedly from the main loop. now_ms must be a millisecond counter. */
ButtonEvent ButtonDebounce_Update(ButtonDebounce *button, uint8_t raw_pressed,
                                  uint32_t now_ms);

uint8_t ButtonDebounce_IsPressed(const ButtonDebounce *button);

#ifdef __cplusplus
}
#endif

#endif
