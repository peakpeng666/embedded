LOCAL_TOOLCHAIN := $(abspath ../.toolchains/arm/usr/bin)
CROSS_COMPILE ?= $(if $(wildcard $(LOCAL_TOOLCHAIN)/arm-none-eabi-gcc),$(LOCAL_TOOLCHAIN)/arm-none-eabi-,arm-none-eabi-)
ARM_CC := $(CROSS_COMPILE)gcc
HOST_CC ?= gcc
CFLAGS := -std=c11 -mcpu=cortex-m4 -mthumb -mfloat-abi=soft -Os -g3 \
          -ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
          -Wall -Wextra -Werror -Isrc -Ivendor/st -Ivendor/arm
LDFLAGS := -mcpu=cortex-m4 -mthumb -mfloat-abi=soft -nostdlib \
           -Tstm32l496_app.ld -Wl,--gc-sections,-Map,build/lab1.map
OBJECTS := build/startup.o build/main.o build/lab_logic.o build/runtime.o

.PHONY: all test clean
all: build/lab1.elf build/lab1.bin build/lab1.hex
	$(CROSS_COMPILE)size build/lab1.elf

build:
	mkdir -p build
build/%.o: src/%.c src/lab_logic.h | build
	$(ARM_CC) $(CFLAGS) -MMD -MP -c $< -o $@
build/startup.o: src/startup.S | build
	$(ARM_CC) $(CFLAGS) -c $< -o $@
build/lab1.elf: $(OBJECTS) stm32l496_app.ld
	$(ARM_CC) $(LDFLAGS) $(OBJECTS) -lgcc -o $@
build/lab1.bin: build/lab1.elf
	$(CROSS_COMPILE)objcopy -O binary $< $@
build/lab1.hex: build/lab1.elf
	$(CROSS_COMPILE)objcopy -O ihex $< $@

test: | build
	$(HOST_CC) -std=c11 -g -Wall -Wextra -Werror -fsanitize=address,undefined \
	    -Isrc src/lab_logic.c tests/test_logic.c -o build/test_logic
	./build/test_logic

clean:
	rm -rf build

-include $(OBJECTS:.o=.d)
