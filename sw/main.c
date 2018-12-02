#include <stdint.h>

#include "samd21.h"
#include "usb.h"
#include "upm.h"
#include "i2c.h"

void sercom1_handler(void) { i2c_irq_handler(); }

int main(void)
{
    uint32_t reg;

    /* Unused PIN Configuration */
    write32(PORT + PORT_DIRSET, UNUSED_PINS);
    write32(PORT + PORT_OUTCLR, UNUSED_PINS);

    /* Configure outputs */
    write32(PORT + PORT_DIRSET, PIN_DUT_USB_EN);
    write32(PORT + PORT_DIRSET, PIN_PACPWRDN_N);
    write32(PORT + PORT_DIRSET, PIN_OUT1_EN);
    write32(PORT + PORT_DIRSET, PIN_OUT2_EN);
    write32(PORT + PORT_DIRSET, PIN_OUT3_EN);
    write32(PORT + PORT_DIRSET, PIN_DUT_DISCHARGE);

    /* Configure inputs */
    write32(PORT + PORT_DIRCLR, PIN_PAC_ALERT_N);
    write32(PORT + PORT_DIRCLR, PIN_DUT_USB_FLAG_N);


    /* Set output default values */
    write32(PORT + PORT_OUTCLR, PIN_DUT_USB_EN);
    write32(PORT + PORT_OUTSET, PIN_PACPWRDN_N);
    write32(PORT + PORT_OUTCLR, PIN_OUT1_EN);
    write32(PORT + PORT_OUTCLR, PIN_OUT2_EN);
    write32(PORT + PORT_OUTCLR, PIN_OUT3_EN);
    write32(PORT + PORT_OUTCLR, PIN_DUT_DISCHARGE);

    /* PAD Mux */
    
    /* PA1 = Sercom1/pad1, PA0 = Sercom1/pad0 */

    write32(PORT + PORT_WRCONFIG, (1 << 30) | (1 << 28) | 
                                  (MUX_D << 24) |
                                  (1 << 16) |
                                  (1 << 0) |
                                  (1 << 1));

    /* PA25 = USB_DP, PA24 = USB_DM */

    write32(PORT + PORT_WRCONFIG, (1 << 30) | (1 << 28) | 
                                  (MUX_G << 24) |
                                  (1 << 16) |
                                  (1 << 24) |
                                  (1 << 25));


    /* Enable SERCOM 1 clock */
    reg = read32(PM + PM_APBCMASK);
    reg |= (1 << 3);
    write32(PM + PM_APBCMASK, reg);
    
    write16(GCLK + GCLK_CLKCTRL, (1 << 14) | GCLK_ID_SERCOMx_SLOW);
    write16(GCLK + GCLK_CLKCTRL, (1 << 14) | GCLK_ID_SERCOM1_CORE);

    write32(NVIC_ISER, (1 << SERCOM1_IRQn));

    i2c_init(SERCOM1);

    while(1) 
    {
        usb_task();
    }
}
