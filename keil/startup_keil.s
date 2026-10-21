; STM32L496 application entry at 0x08010000, for Arm Compiler 5/6.
; Match the GNU startup: 64 KiB initial stack top, 128 vectors, and
; initialize only this application's RW/ZI regions before entering main.
                PRESERVE8
                THUMB

                AREA RESET, DATA, READONLY, ALIGN=9
                EXPORT g_vectors
g_vectors
                DCD 0x20010000
                DCD Reset_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler
                DCD SysTick_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler
                DCD EXTI9_5_IRQHandler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler
                DCD Default_Handler, Default_Handler, Default_Handler, Default_Handler

                AREA |.text|, CODE, READONLY
                IMPORT main
                IMPORT SysTick_Handler
                IMPORT EXTI9_5_IRQHandler
                IMPORT |Load$$RW_IRAM1$$Base|
                IMPORT |Image$$RW_IRAM1$$RW$$Base|
                IMPORT |Image$$RW_IRAM1$$RW$$Limit|
                IMPORT |Image$$RW_IRAM1$$ZI$$Base|
                IMPORT |Image$$RW_IRAM1$$ZI$$Limit|
                EXPORT Reset_Handler
Reset_Handler   PROC
                CPSID i
                LDR r0, =0x20010000
                MSR MSP, r0
                LDR r0, =|Load$$RW_IRAM1$$Base|
                LDR r1, =|Image$$RW_IRAM1$$RW$$Base|
                LDR r2, =|Image$$RW_IRAM1$$RW$$Limit|
copy_data
                CMP r1, r2
                BCS zero_setup
                LDR r3, [r0], #4
                STR r3, [r1], #4
                B copy_data
zero_setup
                LDR r1, =|Image$$RW_IRAM1$$ZI$$Base|
                LDR r2, =|Image$$RW_IRAM1$$ZI$$Limit|
                MOVS r3, #0
zero_bss
                CMP r1, r2
                BCS enter_main
                STR r3, [r1], #4
                B zero_bss
enter_main
                BL main
returned
                B returned
                ENDP

                EXPORT Default_Handler
Default_Handler PROC
                CPSID i
idle
                WFI
                B idle
                ENDP
                ALIGN
                END
