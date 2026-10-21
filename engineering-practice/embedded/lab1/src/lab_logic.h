#ifndef LAB_LOGIC_H
#define LAB_LOGIC_H

#include <stdbool.h>
#include <stdint.h>

#define LAB_DEBOUNCE_MS 20u
#define LAB_POLL_MS 5u
#define LAB_FRAME_MS 300u

typedef enum { LAB_OFF, LAB_COLOR } lab_mode_t;

typedef struct {
    bool stable;
    bool candidate;
    bool pending;
    uint32_t since;
} lab_button_t;

typedef struct {
    lab_mode_t mode;
    uint32_t key0_presses;
    uint32_t key1_presses;
    uint32_t frame_start;
    uint32_t frame;
    lab_button_t key0;
    lab_button_t key1;
} lab_t;

void lab_init(lab_t *lab, uint32_t now, bool key0_down, bool key1_down);
bool lab_poll_key0(lab_t *lab, uint32_t now, bool pressed);
void lab_key1_edge(lab_t *lab, uint32_t when, bool pressed);
bool lab_service_key1(lab_t *lab, uint32_t now, bool sampled_pressed);
uint8_t lab_led_mask(lab_t *lab, uint32_t now);
const char *lab_mode_name(const lab_t *lab);

#endif
