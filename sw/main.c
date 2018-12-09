#include <stdint.h>

#include "samd21.h"
#include "usb.h"
#include "upm.h"
#include "i2c.h"
#include "protocol.h"
#include "pac193x.h"

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
    write32(PORT + PORT_OUTSET, PIN_DUT_USB_EN);
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

    write32(PORT + PORT_WRCONFIG, (1 << 31) | (1 << 30) | (1 << 28) | 
                                  (MUX_G << 24) |
                                  (1 << 16) |
                                  (1 << 8) |
                                  (1 << 9));


    /* Enable SERCOM 1 clock */
    reg = read32(PM + PM_APBCMASK);
    reg |= (1 << 3);
    write32(PM + PM_APBCMASK, reg);
    
    write16(GCLK + GCLK_CLKCTRL, (1 << 14) | GCLK_ID_SERCOMx_SLOW);
    write16(GCLK + GCLK_CLKCTRL, (1 << 14) | GCLK_ID_SERCOM1_CORE);

    //write32(NVIC_ISER, (1 << SERCOM1_IRQn));

    i2c_init(SERCOM1);


    /* Enable and connect USB clock to generator 0 */
    write16(GCLK + GCLK_CLKCTRL, (1 << 14) | GCLK_ID_USB);

    pac193x_init(0x20);

    usb_init(USB);
    struct upm_in in;

    while(1) 
    {
        usb_task();

        if (usb_enumerated()) 
        {
            
            pac193x_refresh();

            for (uint32_t i = 0; i < 0xfff; i++)
                asm("nop");

            for (uint32_t i = 0; i < 4; i++)
            {
                in.Vbus[i] = pac193x_vbus(i);
                in.Vsns[i] = pac193x_vsns(i);
                pac193x_pwr(i, in.Ereg[i]);
            }

            usb_send((uint8_t *) &in, sizeof(struct upm_in));

            if (usb_has_data())
            {
                struct upm_out *out = (struct upm_out *) usb_get_buf();

                if (out->outputs_set & (1 << 0))
                {
                    in.outputs |= (1 << 0);
                    write32(PORT + PORT_OUTCLR, PIN_DUT_DISCHARGE);
                    write32(PORT + PORT_OUTSET, PIN_DUT_USB_EN);
                }

                if (out->outputs_clr & (1 << 0))
                {
                    in.outputs &= ~(1 << 0); 
                    write32(PORT + PORT_OUTSET, PIN_DUT_DISCHARGE);
                    write32(PORT + PORT_OUTCLR, PIN_DUT_USB_EN);
                }


                if (out->outputs_set & (1 << 1))
                {
                    in.outputs |= (1 << 1);
                    write32(PORT + PORT_OUTSET, PIN_OUT1_EN);
                }


                if (out->outputs_clr & (1 << 1))
                {
                    in.outputs &= ~(1 << 1);
                    write32(PORT + PORT_OUTCLR, PIN_OUT1_EN);
                }


                if (out->outputs_set & (1 << 2))
                {
                    in.outputs |= (1 << 2);
                    write32(PORT + PORT_OUTSET, PIN_OUT2_EN);
                }


                if (out->outputs_clr & (1 << 2))
                {
                    in.outputs &= ~(1 << 2);
                    write32(PORT + PORT_OUTCLR, PIN_OUT2_EN);
                }


                if (out->outputs_set & (1 << 3))
                {
                    in.outputs |= (1 << 3);
                    write32(PORT + PORT_OUTSET, PIN_OUT3_EN);
                }


                if (out->outputs_clr & (1 << 3))
                {
                    in.outputs &= ~(1 << 3);
                    write32(PORT + PORT_OUTCLR, PIN_OUT3_EN);
                }

                if (out->counter_reset & (1 << 0))
                {
                    pac193x_reset_counters();
                }

            }

        }
    }
}
