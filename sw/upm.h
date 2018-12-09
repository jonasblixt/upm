/**
 * UPM
 *
 * Copyright (C) 2018 Jonas Persson <jonpe960@gmail.com>
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */

#ifndef __UPM_H__
#define __UPM_H__

#define PIN_SDA            PIN_PA0
#define PIN_SCL            PIN_PA1
#define PIN_PAC_ALERT_N    PIN_PA2
#define PIN_PACPWRDN_N     PIN_PA3
#define PIN_DUT_USB_EN     PIN_PA4
#define PIN_DUT_USB_FLAG_N PIN_PA5
#define PIN_OUT1_EN        PIN_PA6
#define PIN_OUT2_EN        PIN_PA7
#define PIN_OUT3_EN        PIN_PA8
#define PIN_DUT_DISCHARGE  PIN_PA9
#define PIN_XTAL_IN        PIN_PA14
#define PIN_XTAL_OUT       PIN_PA15
#define PIN_USB_DM         PIN_PA24
#define PIN_USB_DP         PIN_PA25
#define PIN_SWO            PIN_PA28
#define PIN_SWCLK          PIN_PA30
#define PIN_SWDIO          PIN_PA31

#define UNUSED_PINS (   PIN_PA10 | \
                        PIN_PA11 | \
                        PIN_PA16 | \
                        PIN_PA17 | \
                        PIN_PA18 | \
                        PIN_PA19 | \
                        PIN_PA22 | \
                        PIN_PA23 | \
                        PIN_PA27)

#endif
