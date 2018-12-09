#
#  UPM CLI
#
# Copyright (C) 2018 Jonas Persson <jonpe960@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
#
#


# Makefile for UPM CLI

TARGET  = upm
PREFIX ?= /usr

CC=$(CROSS_COMPILE)gcc
LD=$(CROSS_COMPILE)ld
AR=$(CROSS_COMPILE)ar
SIZE=$(CROSS_COMPILE)size
OBJCOPY=$(CROSS_COMPILE)objcopy

GIT_VERSION = $(shell git describe --abbrev=4 --dirty --always --tags)
PKG_CONFIG ?= pkg-config
CFLAGS   = -Wall -O2 
CFLAGS  += -I. -I include/ -I ../../
CFLAGS  += -DVERSION=\"$(GIT_VERSION)\"
CFLAGS  += `$(PKG_CONFIG) --cflags libusb-1.0`
CFLAGS  += `$(PKG_CONFIG) --cflags ncurses`

LIBS     =  `$(PKG_CONFIG) --libs libusb-1.0` -luuid
LIBS     += `$(PKG_CONFIG) --libs ncurses` -luuid

LDFLAGS =  

ASM_SRCS = 
C_SRCS   = $(TARGET).c

OBJS     = $(ASM_SRCS:.S=.o) $(C_SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	@echo LINK $@ $(LDFLAGS)
	@$(CC) $(LDFLAGS) $(CFLAGS) $(OBJS) $(LIBS) -o $@

%.o: %.S
	@echo CC $<
	@$(CC) -c $(CFLAGS) $< -o $@
%.o: %.c
	@echo CC $<
	@$(CC) -c $(CFLAGS) $< -o $@

install:
	@install -m 755 $(TARGET) $(PREFIX)/bin

clean: 
	@-rm -rf *.o $(TARGET)  *.map out

