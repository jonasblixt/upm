#ifndef __UPM_H__
#define __UPM_H__

#define PIN_SDA            (1 << 0)
#define PIN_SCL            (1 << 1)
#define PIN_PAC_ALERT_N    (1 << 2)
#define PIN_PACPWRDN_N     (1 << 3)
#define PIN_DUT_USB_EN     (1 << 4)
#define PIN_DUT_USB_FLAG_N (1 << 5)
#define PIN_OUT1_EN        (1 << 6)
#define PIN_OUT2_EN        (1 << 7)
#define PIN_OUT3_EN        (1 << 8)
#define PIN_DUT_DISCHARGE  (1 << 9)
#define PIN_PA10           (1 << 10)
#define PIN_PA11           (1 << 11)
#define PIN_XTAL_IN        (1 << 14)
#define PIN_XTAL_OUT       (1 << 15)
#define PIN_PA16           (1 << 16)
#define PIN_PA17           (1 << 17)
#define PIN_PA18           (1 << 18)
#define PIN_PA19           (1 << 19)
#define PIN_PA22           (1 << 22)
#define PIN_PA23           (1 << 23)
#define PIN_USB_DM         (1 << 24)
#define PIN_USB_DP         (1 << 25)
#define PIN_PA27           (1 << 27)
#define PIN_SWO            (1 << 28)
#define PIN_SWCLK          (1 << 30)
#define PIN_SWDIO          (1 << 31)

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
