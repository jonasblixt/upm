#include <stdbool.h>
#include "samd21.h"
#include "upm.h"
#include "pac193x.h"
#include "i2c.h"

static uint8_t addr;

uint32_t pac193x_init(uint8_t _addr)
{

    addr = _addr;

    /* PAC1934 needs 14ms before it is possible to communicate */
    for (uint32_t i = 0; i < 0xfffff; i++)
        asm("nop");

    i2c_start(addr);
    i2c_write_byte(0x01);
    i2c_start(addr);
    i2c_write_byte(0);
    i2c_stop();


    i2c_start(addr);
    i2c_write_byte(0x1E);
    i2c_stop();
    return 0;
}

void pac193x_refresh(void)
{
    i2c_start(addr);
    i2c_write_byte(0x1F);
    i2c_stop();
}


void pac193x_reset_counters(void)
{
    i2c_start(addr);
    i2c_write_byte(0x00);
    i2c_stop();
}


uint16_t pac193x_vbus(uint8_t ch)
{
    uint8_t b0, b1;

    i2c_start(addr);
    i2c_write_byte(0x0f + (ch & 0x03));
    i2c_start(addr | 1);
    i2c_read_byte(&b0, false);
    i2c_read_byte(&b1, true);
    i2c_stop();

    return (b0 << 8) | b1;
}

uint16_t pac193x_vsns(uint8_t ch)
{
    uint8_t b0, b1;

    i2c_start(addr);
    i2c_write_byte(0x13 + (ch & 0x03));
    i2c_start(addr | 1);
    i2c_read_byte(&b0, false);
    i2c_read_byte(&b1, true);
    i2c_stop();

    return (b0 << 8) | b1;
}

void pac193x_pwr(uint8_t ch, uint8_t *out)
{

    i2c_start(addr);
    i2c_write_byte(0x03 + (ch & 0x03));
    i2c_start(addr | 1);
    i2c_read_byte(&out[5], false);
    i2c_read_byte(&out[4], false);
    i2c_read_byte(&out[3], false);
    i2c_read_byte(&out[2], false);
    i2c_read_byte(&out[1], false);
    i2c_read_byte(&out[0], true);
    i2c_stop();
    
}
