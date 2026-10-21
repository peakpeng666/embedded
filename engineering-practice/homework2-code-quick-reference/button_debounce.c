#include "button_debounce.h"

void ButtonDebounce_Init(ButtonDebounce *button, uint8_t initial_pressed,
                         uint32_t debounce_ms, uint32_t now_ms)
{
    uint8_t pressed = (initial_pressed != 0U) ? 1U : 0U;

    button->changed_at_ms = now_ms;
    button->debounce_ms = debounce_ms;
    button->stable_pressed = pressed;
    button->candidate_pressed = pressed;
}

ButtonEvent ButtonDebounce_Update(ButtonDebounce *button, uint8_t raw_pressed,
                                  uint32_t now_ms)
{
    uint8_t pressed = (raw_pressed != 0U) ? 1U : 0U;

    if (pressed != button->candidate_pressed)
    {
        button->candidate_pressed = pressed;
        button->changed_at_ms = now_ms;
    }

    if ((button->candidate_pressed != button->stable_pressed) &&
        ((uint32_t)(now_ms - button->changed_at_ms) >= button->debounce_ms))
    {
        button->stable_pressed = button->candidate_pressed;
        return (button->stable_pressed != 0U)
                   ? BUTTON_EVENT_PRESSED
                   : BUTTON_EVENT_RELEASED;
    }

    return BUTTON_EVENT_NONE;
}

uint8_t ButtonDebounce_IsPressed(const ButtonDebounce *button)
{
    return button->stable_pressed;
}
