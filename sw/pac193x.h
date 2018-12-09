#ifndef __PAC193X_H__
#define __PAC193X_H__

#include <stdint.h>

uint32_t pac193x_init(uint8_t _addr);
void pac193x_refresh(void);
uint16_t pac193x_vbus(uint8_t ch);
uint16_t pac193x_vsns(uint8_t ch);
void pac193x_pwr(uint8_t ch, uint8_t *out);
void pac193x_reset_counters(void);

#endif
