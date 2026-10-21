#include "lab_logic.h"

static void restart_pattern(lab_t *lab, uint32_t now)
{
    lab->frame = 0;
    lab->frame_start = now;
}

void lab_init(lab_t *lab, uint32_t now, bool key0_down, bool key1_down)
{
    *lab = (lab_t){.mode = LAB_OFF};
    lab->mode = LAB_OFF;
    lab->frame_start = now;
    lab->key0.stable = lab->key0.candidate = key0_down;
    lab->key1.stable = lab->key1.candidate = key1_down;
}

/* This function must be called regularly: KEY0 has no EXTI configuration. */
bool lab_poll_key0(lab_t *lab, uint32_t now, bool pressed)
{
    lab_button_t *key = &lab->key0;
    if (pressed != key->candidate) {
        key->candidate = pressed;
        key->since = now;
    }
    if (pressed != key->stable && (uint32_t)(now - key->since) >= LAB_DEBOUNCE_MS) {
        key->stable = pressed;
        if (pressed) {
            lab->key0_presses++;
            /* A held stop key takes priority; a new KEY0 press is required
               after releasing it, so the lamp never restarts by itself. */
            if (!lab->key1.stable) {
                lab->mode = LAB_COLOR;
                restart_pattern(lab, now);
            }
            return true;
        }
    }
    return false;
}

/* Called by the main loop only when the real EXTI handler has recorded an edge. */
void lab_key1_edge(lab_t *lab, uint32_t when, bool pressed)
{
    lab->key1.candidate = pressed;
    lab->key1.since = when;
    lab->key1.pending = true;
}

bool lab_service_key1(lab_t *lab, uint32_t now, bool sampled_pressed)
{
    lab_button_t *key = &lab->key1;
    if (!key->pending) {
        return false; /* A pin-level change without an interrupt cannot trigger KEY1. */
    }
    if (sampled_pressed != key->candidate) {
        key->candidate = sampled_pressed;
        key->since = now;
        return false;
    }
    if ((uint32_t)(now - key->since) < LAB_DEBOUNCE_MS) {
        return false;
    }
    key->pending = false;
    if (key->stable != sampled_pressed) {
        key->stable = sampled_pressed;
        if (sampled_pressed) {
            lab->key1_presses++;
            lab->mode = LAB_OFF;
            restart_pattern(lab, now);
            return true;
        }
    }
    return false;
}

uint8_t lab_led_mask(lab_t *lab, uint32_t now)
{
    /* Seven nonzero RGB combinations, each separated by an OFF frame. */
    static const uint8_t blink[] = {
        1u, 0u, 2u, 0u, 4u, 0u, 3u, 0u, 6u, 0u, 5u, 0u, 7u, 0u
    };
    if (lab->mode == LAB_OFF) {
        return 0u;
    }
    const uint32_t period = LAB_FRAME_MS;
    const uint32_t length = sizeof blink / sizeof blink[0];
    uint32_t elapsed_frames = (uint32_t)(now - lab->frame_start) / period;
    lab->frame = (lab->frame + elapsed_frames % length) % length;
    lab->frame_start += elapsed_frames * period;
    return blink[lab->frame];
}

const char *lab_mode_name(const lab_t *lab)
{
    static const char *const names[] = {"OFF", "COLOR"};
    return names[lab->mode];
}
