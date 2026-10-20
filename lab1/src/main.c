/*
 * STM32L496VET6, Pandora: existing RGB channels and two onboard buttons.
 * No flash programming, option-byte access, or bootloader update code.
 */
#include "stm32l496xx.h"
#include "lab_logic.h"

#define LED_PINS ((1u << 7) | (1u << 8) | (1u << 9))
#define KEY0_PIN (1u << 10)
#define KEY1_PIN (1u << 9)
#define TX_SIZE 512u

uint32_t SystemCoreClock = 16000000u;
static volatile uint32_t milliseconds;
static volatile uint32_t irq_time;
static volatile uint32_t irq_count;
static volatile bool irq_pending;
static volatile bool irq_pressed;
static char tx_buffer[TX_SIZE];
static uint32_t tx_write, tx_read, tx_dropped;
static lab_t lab;

static bool key0_down(void) { return (GPIOD->IDR & KEY0_PIN) == 0u; }
static bool key1_down(void) { return (GPIOD->IDR & KEY1_PIN) == 0u; }

void SysTick_Handler(void) { milliseconds++; }

void EXTI9_5_IRQHandler(void)
{
    if ((EXTI->PR1 & KEY1_PIN) != 0u) {
        EXTI->PR1 = KEY1_PIN;
        irq_time = milliseconds;
        irq_pressed = key1_down();
        irq_count++;
        irq_pending = true;
    }
}

static void uart_put(char ch)
{
    uint32_t next = (tx_write + 1u) % TX_SIZE;
    if (next != tx_read) {
        tx_buffer[tx_write] = ch;
        tx_write = next;
    } else {
        tx_dropped++;
    }
}

static void uart_text(const char *text)
{
    while (*text != '\0') {
        uart_put(*text++);
    }
}

static void uart_number(uint32_t number)
{
    char digits[10];
    unsigned count = 0;
    do {
        digits[count++] = (char)('0' + number % 10u);
        number /= 10u;
    } while (number != 0u);
    while (count != 0u) {
        uart_put(digits[--count]);
    }
}

static void print_status(const char *event)
{
    uart_text(event);
    uart_text(" mode="); uart_text(lab_mode_name(&lab));
    uart_text(" poll_presses="); uart_number(lab.key0_presses);
    uart_text(" exti_presses="); uart_number(lab.key1_presses);
    uart_text(" irq_edges="); uart_number(irq_count);
    uart_text(" tx_dropped="); uart_number(tx_dropped);
    uart_text("\r\n");
}

static bool same_text(const char *a, const char *b)
{
    while (*a != '\0' && *a == *b) { a++; b++; }
    return *a == *b;
}

static void uart_service(void)
{
    static char command[24];
    static unsigned used;
    static bool overflow;
    uint32_t status = USART1->ISR;
    if (status & (USART_ISR_ORE | USART_ISR_FE | USART_ISR_NE)) {
        USART1->ICR = USART_ICR_ORECF | USART_ICR_FECF | USART_ICR_NCF;
        used = 0;
        overflow = false;
    }
    if ((status & USART_ISR_RXNE) != 0u) {
        char ch = (char)USART1->RDR;
        if (ch == '\r' || ch == '\n') {
            command[used] = '\0';
            if (overflow) {
                uart_text("Command too long. Use status or help.\r\n");
            } else if (used == 0u || same_text(command, "status")) {
                print_status("STATUS");
            } else if (same_text(command, "help")) {
                uart_text("status: mode/counters; KEY0 POLL: RGB cycle; KEY1 EXTI: all OFF\r\n");
            } else {
                uart_text("Unknown command. Use status or help.\r\n");
            }
            used = 0;
            overflow = false;
        } else if (ch == '\b' || ch == 0x7f) {
            if (used > 0u) { used--; }
        } else if (ch >= ' ' && ch <= '~') {
            if (used + 1u < sizeof command) { command[used++] = ch; }
            else { overflow = true; }
        }
    }
    while (tx_read != tx_write && (USART1->ISR & USART_ISR_TXE) != 0u) {
        USART1->TDR = (uint8_t)tx_buffer[tx_read];
        tx_read = (tx_read + 1u) % TX_SIZE;
    }
}

static void hardware_init(void)
{
    __disable_irq();
    SysTick->CTRL = 0u;
    for (unsigned i = 0; i < 8; i++) {
        NVIC->ICER[i] = 0xffffffffu;
        NVIC->ICPR[i] = 0xffffffffu;
    }
    SCB->ICSR = SCB_ICSR_PENDSTCLR_Msk | SCB_ICSR_PENDSVCLR_Msk;
    SCB->SCR &= ~(SCB_SCR_SLEEPDEEP_Msk | SCB_SCR_SLEEPONEXIT_Msk);
    SCB->VTOR = 0x08010000u;
    __DSB();
    __ISB();

    /* Switch to internal HSI16; do not depend on the external crystal or PLL. */
    RCC->CR |= RCC_CR_HSION;
    while ((RCC->CR & RCC_CR_HSIRDY) == 0u) {}
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_HSI;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_HSI) {}
    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    SystemCoreClock = 16000000u;
    /* Retain the bootloader's flash wait states; lowering frequency is safe. */

    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIODEN | RCC_AHB2ENR_GPIOEEN;
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN | RCC_APB2ENR_USART1EN;
    (void)RCC->APB2ENR;

    /* Preload OFF before changing the common-anode RGB pins to outputs. */
    GPIOE->BSRR = LED_PINS;
    GPIOE->OTYPER &= ~LED_PINS;
    GPIOE->OSPEEDR &= ~((3u << 14) | (3u << 16) | (3u << 18));
    GPIOE->PUPDR &= ~((3u << 14) | (3u << 16) | (3u << 18));
    GPIOE->MODER = (GPIOE->MODER & ~((3u << 14) | (3u << 16) | (3u << 18)))
                  | (1u << 14) | (1u << 16) | (1u << 18);
    GPIOD->MODER &= ~((3u << 18) | (3u << 20));
    GPIOD->PUPDR = (GPIOD->PUPDR & ~((3u << 18) | (3u << 20)))
                  | (1u << 18) | (1u << 20);

    GPIOA->OTYPER &= ~((1u << 9) | (1u << 10));
    GPIOA->PUPDR = (GPIOA->PUPDR & ~((3u << 18) | (3u << 20)))
                  | (1u << 18) | (1u << 20);
    GPIOA->OSPEEDR &= ~((3u << 18) | (3u << 20));
    GPIOA->AFR[1] = (GPIOA->AFR[1] & ~((15u << 4) | (15u << 8)))
                   | (7u << 4) | (7u << 8);
    GPIOA->MODER = (GPIOA->MODER & ~((3u << 18) | (3u << 20)))
                  | (2u << 18) | (2u << 20);
    RCC->CCIPR &= ~RCC_CCIPR_USART1SEL;
    USART1->CR1 = 0u;
    USART1->CR2 = 0u;
    USART1->CR3 = 0u;
    USART1->BRR = 139u; /* 16 MHz / 115200, nearest integer; about -0.08%. */
    USART1->ICR = USART_ICR_ORECF | USART_ICR_FECF | USART_ICR_NCF | USART_ICR_IDLECF;
    USART1->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;

    /* KEY0/PD10 explicitly has no interrupt. KEY1/PD9 uses both edges:
       falling requests a press, rising rearms release after debounce. */
    const uint32_t exti_group = (0x1fu << 5) | KEY0_PIN;
    EXTI->IMR1 &= ~exti_group;
    EXTI->RTSR1 &= ~exti_group;
    EXTI->FTSR1 &= ~exti_group;
    SYSCFG->EXTICR[2] = (SYSCFG->EXTICR[2] & ~(15u << 4)) | (3u << 4);
    lab_init(&lab, milliseconds, key0_down(), key1_down());
    EXTI->PR1 = exti_group;
    EXTI->RTSR1 |= KEY1_PIN;
    EXTI->FTSR1 |= KEY1_PIN;
    EXTI->IMR1 |= KEY1_PIN;
    NVIC_SetPriority(EXTI9_5_IRQn, 2u);
    NVIC_ClearPendingIRQ(EXTI9_5_IRQn);
    NVIC_EnableIRQ(EXTI9_5_IRQn);
    (void)SysTick_Config(SystemCoreClock / 1000u);
    __enable_irq();
}

int main(void)
{
    hardware_init();
    uart_text("\r\nLAB1 STM32L496 RGB COLOR / EXTI OFF; 115200 8N1\r\n");
    uart_text("KEY0 POLL: R/G/B/Y/C/M/W with OFF gaps, 300ms per frame\r\n");
    uart_text("KEY1 EXTI: all OFF\r\n");
    uart_text("Release KEY1 then press KEY0 to restart at red; UART: status or help\r\n");
    print_status("BOOT");
    uint32_t last_poll = milliseconds;
    uint8_t previous_mask = 0u;
    for (;;) {
        uint32_t now = milliseconds;
        if ((uint32_t)(now - last_poll) >= LAB_POLL_MS) {
            last_poll = now;
            if (lab_poll_key0(&lab, now, key0_down())) {
                print_status("KEY0 POLL");
            }
        }

        /* Copy the ISR mailbox atomically; process debounce and LEDs in thread mode. */
        __disable_irq();
        bool pending = irq_pending;
        uint32_t when = irq_time;
        bool pressed = irq_pressed;
        irq_pending = false;
        __enable_irq();
        if (pending) {
            lab_key1_edge(&lab, when, pressed);
        }
        /* An IRQ may have occurred after the time sampled at loop entry. */
        now = milliseconds;
        if (lab.key1.pending && lab_service_key1(&lab, now, key1_down())) {
            print_status("KEY1 EXTI");
        }
        uint8_t mask = lab_led_mask(&lab, now);
        if (mask != previous_mask) {
            uint32_t on = ((uint32_t)mask << 7) & LED_PINS;
            GPIOE->BSRR = (LED_PINS & ~on) | (on << 16);
            previous_mask = mask;
        }
        uart_service();
        /* USART RX is polled, so do not sleep until the next 1 ms tick:
           at 115200 baud a byte arrives about every 87 us. */
    }
}
