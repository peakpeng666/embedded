#include "lab_logic.h"
#include <assert.h>
#include <stdio.h>

static void poll_press(lab_t *lab, uint32_t start)
{
    assert(!lab_poll_key0(lab, start, true));
    assert(!lab_poll_key0(lab, start + 19u, true));
    assert(lab_poll_key0(lab, start + 20u, true));
}

static void poll_release(lab_t *lab, uint32_t start)
{
    assert(!lab_poll_key0(lab, start, false));
    assert(!lab_poll_key0(lab, start + 20u, false));
}

static void irq_press(lab_t *lab, uint32_t start)
{
    lab_key1_edge(lab, start, true);
    assert(!lab_service_key1(lab, start + 19u, true));
    assert(lab_service_key1(lab, start + 20u, true));
}

static void irq_release(lab_t *lab, uint32_t start)
{
    lab_key1_edge(lab, start, false);
    assert(!lab_service_key1(lab, start + 20u, false));
}

static void test_start_and_held_keys(void)
{
    lab_t lab;
    lab_init(&lab, 0u, true, true);
    assert(lab_led_mask(&lab, 0u) == 0u);
    assert(!lab_poll_key0(&lab, 100u, true));
    assert(!lab_service_key1(&lab, 100u, true));
    poll_release(&lab, 110u);
    irq_release(&lab, 110u);
    poll_press(&lab, 150u);
    irq_press(&lab, 150u);
    assert(lab.key0_presses == 1u && lab.key1_presses == 1u);
    puts("PASS startup is OFF; held-at-start buttons require release");
}

static void test_poll_debounce_and_direct_selection(void)
{
    lab_t lab;
    lab_init(&lab, 0u, false, false);
    const bool bounce[] = {true, false, true, false, true};
    for (unsigned i = 0; i < 5; i++) {
        assert(!lab_poll_key0(&lab, i * 5u, bounce[i]));
    }
    assert(!lab_poll_key0(&lab, 39u, true));
    assert(lab_poll_key0(&lab, 40u, true));
    assert(lab.mode == LAB_COLOR);
    for (unsigned i = 45; i <= 2000; i += 5) {
        assert(!lab_poll_key0(&lab, i, true));
    }
    assert(lab.key0_presses == 1u);
    for (unsigned i = 0; i < 3; i++) {
        poll_release(&lab, 2100u + i * 100u);
        poll_press(&lab, 2140u + i * 100u);
    }
    assert(lab.mode == LAB_COLOR && lab.key0_presses == 4u);
    puts("PASS KEY0 bounce, long hold, release rearm, COLOR restart");
}

static void test_irq_debounce_and_dependency(void)
{
    lab_t lab;
    lab_init(&lab, 0u, false, false);
    poll_press(&lab, 0u);
    assert(!lab_service_key1(&lab, 100u, true));
    assert(lab.mode == LAB_COLOR); /* A level without EXTI cannot stop the lamp. */
    lab_key1_edge(&lab, 100u, true);
    lab_key1_edge(&lab, 105u, false);
    lab_key1_edge(&lab, 110u, true);
    assert(!lab_service_key1(&lab, 129u, true));
    assert(lab_service_key1(&lab, 130u, true));
    assert(lab.mode == LAB_OFF && lab.key1_presses == 1u);
    assert(!lab_service_key1(&lab, 2000u, true));
    lab_key1_edge(&lab, 2010u, true);
    assert(!lab_service_key1(&lab, 2030u, true));
    irq_release(&lab, 2100u);
    irq_press(&lab, 2200u);
    assert(lab.mode == LAB_OFF && lab.key1_presses == 2u);
    puts("PASS KEY1 needs EXTI, stops the lamp, counts one event per press");
}

static void test_irq_level_changed_during_debounce(void)
{
    lab_t lab;
    lab_init(&lab, 0u, false, false);
    poll_press(&lab, 0u);
    lab_key1_edge(&lab, 100u, true);
    assert(!lab_service_key1(&lab, 120u, false));
    assert(!lab_service_key1(&lab, 140u, false));
    assert(lab.key1_presses == 0u);
    assert(lab.mode == LAB_COLOR);
    puts("PASS stale EXTI candidate cannot commit a false press");
}

static void test_patterns_and_switching(void)
{
    lab_t lab;
    lab_init(&lab, 0u, false, false);
    poll_press(&lab, 0u);
    const uint8_t expected[] = {1, 0, 2, 0, 4, 0, 3, 0, 6, 0, 5, 0, 7, 0};
    uint8_t seen = 0;
    for (unsigned i = 0; i < 28; i++) {
        uint32_t start = 20u + i * LAB_FRAME_MS;
        uint8_t mask = expected[i % 14];
        assert(lab_led_mask(&lab, start) == mask);
        assert(lab_led_mask(&lab, start + LAB_FRAME_MS - 1) == mask);
        seen |= (uint8_t)(1u << mask);
    }
    assert(seen == 0xff); /* All seven colours and OFF actually occur. */
    irq_press(&lab, 8500u);
    assert(lab_led_mask(&lab, 8520u) == 0u);
    assert(lab_led_mask(&lab, 9000u) == 0u);
    poll_release(&lab, 9100u);
    poll_press(&lab, 9140u); /* Held KEY1 inhibits restarting. */
    assert(lab.mode == LAB_OFF);
    irq_release(&lab, 9200u);
    assert(lab_led_mask(&lab, 9250u) == 0u); /* Release does not restart. */
    poll_release(&lab, 9300u);
    poll_press(&lab, 9340u);
    assert(lab.mode == LAB_COLOR && lab_led_mask(&lab, 9360u) == 1u);
    puts("PASS all seven colours, OFF gaps, EXTI stop, held-stop priority and red restart");
}

static void test_simultaneous_and_time_wrap(void)
{
    lab_t lab;
    uint32_t start = UINT32_MAX - 10u;
    lab_init(&lab, start, false, false);
    assert(!lab_poll_key0(&lab, start, true));
    lab_key1_edge(&lab, start, true);
    uint32_t accepted = start + 20u;
    assert(lab_poll_key0(&lab, accepted, true));
    assert(lab_service_key1(&lab, accepted, true));
    assert(lab.mode == LAB_OFF);
    assert(lab_led_mask(&lab, accepted) == 0u);
    assert(lab_led_mask(&lab, accepted + 300u) == 0u);
    irq_release(&lab, accepted + 350u);
    poll_release(&lab, accepted + 400u);
    poll_press(&lab, accepted + 440u);
    uint32_t restart = accepted + 460u;
    assert(lab.mode == LAB_COLOR);
    assert(lab_led_mask(&lab, restart) == 1u);
    assert(lab_led_mask(&lab, restart + LAB_FRAME_MS * 1000004u) == 7u);
    puts("PASS simultaneous keys, 32-bit clock wrap and delayed-loop catch-up");
}

int main(void)
{
    test_start_and_held_keys();
    test_poll_debounce_and_direct_selection();
    test_irq_debounce_and_dependency();
    test_irq_level_changed_during_debounce();
    test_patterns_and_switching();
    test_simultaneous_and_time_wrap();
    puts("All six requirement-focused test groups passed.");
    return 0;
}
