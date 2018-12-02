#include "samd21.h"
#include "upm.h"
#include "i2c.h"

static uint32_t base;

void i2c_irq_handler(void)
{
    uint8_t isr = read8(base + I2C_INTFLAG);

    if (isr & I2C_IRQ_MB) {
    }

    if (isr & I2C_IRQ_SB) {
    }


    write8(base + I2C_INTFLAG, isr);
}

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

uint32_t i2c_read(uint8_t i2c_addr, uint8_t device_addr, uint8_t *buf,  
                    uint16_t sz)
{
    


    return 0;
}
