#ifndef __I2C_H__
#define __I2C_H__

#include <stdint.h>

void i2c_init(uint32_t _base);
void i2c_irq_handler(void);

#endif
