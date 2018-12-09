#ifndef __PROTOCOL_H__
#define __PROTOCOL_H__

#include <stdint.h>

struct upm_out {
    uint32_t counter_reset;
    uint32_t outputs_set;
    uint32_t outputs_clr;
} __attribute__ ((packed));

struct upm_in {
    uint16_t Vbus[4];
    uint16_t Vsns[4];
    uint8_t Ereg[4][6];
    uint32_t outputs;
} __attribute__ ((packed)); 

#endif
