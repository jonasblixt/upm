/**
 * UPM
 *
 * Copyright (C) 2018 Jonas Persson <jonpe960@gmail.com>
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */

#include <stdint.h>
#include <stdbool.h>
#include "samd21.h"
#include "upm.h"
#include "i2c.h"

#define I2C_BUFFER_SIZE 16

static uint32_t base;

void i2c_init(uint32_t _base)
{
    uint32_t reg;

    base = _base;
    /* Set I2C Master mode */

    write32(base + I2C_CTRLA, 1);
    while((read32(base + I2C_CTRLA) & 1) == 1);

   
    write32(base + I2C_CTRLB, (1 << 8));
    while (read32(base + I2C_SYNCBUSY) & 7);

   /* Configure baud rate 
     * 
     * f_ref = 48MHz, f_Baud = 100kHz
     *
     * BAUD = f_ref / (2 * f_Baud) - 1 = 239
     * 
     */
    write32(base + I2C_BAUD, 239);
    
    while (read32(base + I2C_SYNCBUSY) & 7);
 
    /* Enable I2C Master mode */
    write32(base + I2C_CTRLA, (0x03 << 20) | (0x05 << 2) | (1 << 1));

    while (read32(base + I2C_SYNCBUSY) & 7);

    reg = read16(base + I2C_STATUS);
    reg |= (1 << 4);
    write16(base + I2C_STATUS, reg);

    while (read32(base + I2C_SYNCBUSY) & 7);

    /* Enable IRQ's */
    write8(base+I2C_INTSET, 0x03);
    while (read32(base + I2C_SYNCBUSY) & 7);

}


uint32_t i2c_start(uint8_t addr)
{
    uint32_t reg;

    write8(base + I2C_INTFLAG, I2C_IRQ_ERR);

    write32(base + I2C_ADDR, addr);

    while (!(read8(base + I2C_INTFLAG) & 0x03));

    reg = read16(base + I2C_STATUS);

    if ( (reg & 0x02) || (reg & 1) )
    {
        reg = read32(base + I2C_CTRLB);
        reg |= (3 << 16);
        write32(base + I2C_CTRLB, reg);
        return 1;
    }

    return 0;
}

uint32_t i2c_stop(void)
{
    uint32_t reg;


    if (read8(base + I2C_INTFLAG) & 0x03)
    {
        reg = read32(base + I2C_CTRLB);
        reg |= (3 << 16);
        write32(base + I2C_CTRLB, reg);
    }

    return 0;
}

uint32_t i2c_read_byte(uint8_t *b, bool last)
{
    uint32_t reg;

    while(1)
    {
        reg = read8(base + I2C_INTFLAG);

        if (reg & I2C_IRQ_SB)
            break;
        
        if ((reg & I2C_IRQ_MB) || (reg & I2C_IRQ_ERR))
            return 1;
    }

    reg = read32(base + I2C_CTRLB);

    if (last) 
        reg |= (1 << 18) | (3 << 16);
    else
        reg &= ~(1 << 18);
    
    write32(base + I2C_CTRLB, reg);
    
    *b = read8(base + I2C_DATA);

    return 0;
}

uint32_t i2c_write_byte(uint8_t b)
{
    uint32_t reg;

    write32(base + I2C_DATA, b);

    while(1)
    {
        reg = read8(base + I2C_INTFLAG);

        if (reg & I2C_IRQ_MB)
            break;
        
        if ((reg & I2C_IRQ_SB) || (reg & I2C_IRQ_ERR))
            return 1;
    }
    
    reg = read8(base + I2C_STATUS);

    if (reg & 0x04)
    {
        reg = read32(base + I2C_CTRLB);
        reg |= (3 << 16);
        write32(base + I2C_CTRLB, reg);
        return 1;
    }

    return 0;
}
