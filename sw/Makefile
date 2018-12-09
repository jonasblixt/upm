# Makefile for UPM

TARGET  = upm

CROSS_COMPILE ?= arm-eabi-


CC=$(CROSS_COMPILE)gcc
LD=$(CROSS_COMPILE)ld
AR=$(CROSS_COMPILE)ar
SIZE=$(CROSS_COMPILE)size
STRIP=$(CROSS_COMPILE)strip
OBJCOPY=$(CROSS_COMPILE)objcopy

GIT_VERSION = $(shell git describe --abbrev=4 --dirty --always --tags)

CFLAGS   = -Wall -Wextra -Wunused-result -O0 -g
CFLAGS  += -nostdlib -nostartfiles -mthumb -march=armv6-m -mtune=cortex-m0plus
CFLAGS  += -I. -I include/ -Wimplicit-fallthrough=0
CFLAGS  += -I CMSIS/CMSIS/Include
CFLAGS  += -D__STARTUP_CLEAR_BSS -D__NO_SYSTEM_INIT
CFLAGS  += -D__HEAP_SIZE=0 -D__STACK_SIZE=0x100
CFLAGS  += -DVERSION=\"$(GIT_VERSION)\" 

LDFLAGS =
ASM_SRCS = 
C_SRCS   = main.c init.c usb.c i2c.c string.c pac193x.c

LDFLAGS += -Wl,-Tlink.lds -Wl,--build-id=none $(CFLAGS)

OBJS     = $(ASM_SRCS:.S=.o) $(C_SRCS:.c=.o) 

all: $(TARGET).bin

showsize:
	@echo "VERSION = $(GIT_VERSION)"
	@$(SIZE) -A $<

$(TARGET).bin: $(TARGET)
	@echo OBJCOPY $< $@
	@$(OBJCOPY) -O binary -R .comment $< $@

$(TARGET): $(OBJS)
	@echo LINK $@
	@$(CC) $(LDFLAGS) $(OBJS) $(LIBS) -o $@

%.o: %.S
	@echo CC $<
	@$(CC) -c $(CFLAGS) $< -o $@

%.o: %.c
	@echo CC $<
	@$(CC) -c $(CFLAGS) $< -o $@

clean: 
	@-rm -rf *.o $(TARGET) $(TARGET).bin *.map out
	@-rm -f $(OBJS)

