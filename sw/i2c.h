/**
 * UPM
 *
 * Copyright (C) 2018 Jonas Persson <jonpe960@gmail.com>
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */

#ifndef __I2C_H__
#define __I2C_H__

#include <stdint.h>
#include <stdbool.h>

/* SERCOM / I2C Master */

#define I2C_CTRLA            0x00
#define I2C_CTRLB            0x04
#define I2C_BAUD             0x0C
#define I2C_DATA             0x28
#define I2C_STATUS           0x1A
#define I2C_SYNCBUSY         0x1C
#define I2C_ADDR             0x24
#define I2C_INTSET           0x16
#define I2C_INTFLAG          0x18

#define I2C_IRQ_MB           0x01
#define I2C_IRQ_SB           0x02
#define I2C_IRQ_ERR          0x80


void i2c_init(uint32_t _base);
uint32_t i2c_write_byte(uint8_t b);
uint32_t i2c_read_byte(uint8_t *b, bool last);
uint32_t i2c_stop(void);
uint32_t i2c_start(uint8_t addr);


#endif
