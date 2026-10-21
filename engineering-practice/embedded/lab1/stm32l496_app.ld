/* Existing board bootloader occupies 0x08000000..0x0800ffff.
   This image is linked only for the application region. */
ENTRY(Reset_Handler)
MEMORY {
    FLASH (rx)  : ORIGIN = 0x08010000, LENGTH = 448K
    /* Deliberately use only the first 64 KiB of SRAM1. This also keeps the
       initial SP in the range used by the original board's application. */
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 64K
}
_estack = ORIGIN(RAM) + LENGTH(RAM);
SECTIONS {
    .isr_vector : { KEEP(*(.isr_vector)) } > FLASH
    .text : { *(.text*) *(.rodata*) . = ALIGN(4); } > FLASH
    .ARM.exidx : { *(.ARM.exidx*) } > FLASH
    _sidata = LOADADDR(.data);
    .data : {
        . = ALIGN(4); _sdata = .; *(.data*) . = ALIGN(4); _edata = .;
    } > RAM AT> FLASH
    .bss (NOLOAD) : {
        . = ALIGN(4); _sbss = .; *(.bss*) *(COMMON) . = ALIGN(4); _ebss = .;
    } > RAM
    /DISCARD/ : { *(.comment*) *(.note*) }
    ASSERT(_ebss + 4096 <= _estack, "Less than 4 KiB stack space remains")
    ASSERT(ADDR(.isr_vector) == 0x08010000, "Application vector address changed")
}
