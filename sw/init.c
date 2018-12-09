#include <stdint.h>
#include "samd21.h"

extern uint32_t _etext;
extern uint32_t _srelocate;
extern uint32_t _erelocate;
extern uint32_t _sbss;
extern uint32_t _ebss;
extern uint32_t _sstack;
extern uint32_t _estack;

extern int main(void);

#ifndef __STACK_SIZE
#define __STACK_SIZE 1024
#endif

uint8_t stack[__STACK_SIZE] __attribute__ ((section(".stack")));

/* Default empty handler */
void dummy_handler(void);

/* Cortex-M0+ core handlers */
void nmi_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void hardfault_handler       ( void ) __attribute__ ((weak, alias("dummy_handler")));
void svc_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void pendsv_handler          ( void ) __attribute__ ((weak, alias("dummy_handler")));
void systick_handler         ( void ) __attribute__ ((weak, alias("dummy_handler")));

/* Peripherals handlers */
void pm_handler              ( void ) __attribute__ ((weak, alias("dummy_handler")));
void sysctrl_handler         ( void ) __attribute__ ((weak, alias("dummy_handler")));
void wdt_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void rtc_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void eic_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void nvmctrl_handler         ( void ) __attribute__ ((weak, alias("dummy_handler")));
void dmac_handler            ( void ) __attribute__ ((weak, alias("dummy_handler")));
void usb_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void evsys_handler           ( void ) __attribute__ ((weak, alias("dummy_handler")));
void sercom0_handler         ( void ) __attribute__ ((weak, alias("dummy_handler")));
void sercom1_handler         ( void ) __attribute__ ((weak, alias("dummy_handler")));
void sercom2_handler         ( void ) __attribute__ ((weak, alias("dummy_handler")));
void sercom3_handler         ( void ) __attribute__ ((weak, alias("dummy_handler")));
void sercom4_handler         ( void ) __attribute__ ((weak, alias("dummy_handler")));
void sercom5_handler         ( void ) __attribute__ ((weak, alias("dummy_handler")));
void tcc0_handler            ( void ) __attribute__ ((weak, alias("dummy_handler")));
void tcc1_handler            ( void ) __attribute__ ((weak, alias("dummy_handler")));
void tcc2_handler            ( void ) __attribute__ ((weak, alias("dummy_handler")));
void tc3_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void tc4_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void tc5_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void tc6_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void tc7_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void adc_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void ac_handler              ( void ) __attribute__ ((weak, alias("dummy_handler")));
void dac_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void ptc_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));
void i2s_handler             ( void ) __attribute__ ((weak, alias("dummy_handler")));

void dummy_handler(void)
{
    while(1)
        asm("nop");
}

void reset_handler(void)
{
    uint32_t *pSrc, *pDest;
    uint32_t reg;

    /* Initialize the relocate segment */
    pSrc = &_etext;
    pDest = &_srelocate;

    if (pSrc != pDest) {
            for (; pDest < &_erelocate;) {
                    *pDest++ = *pSrc++;
            }
    }

    /* Clear the zero segment */
    for (pDest = &_sbss; pDest < &_ebss;) {
            *pDest++ = 0;
    }

    /* Configure flash wait state */
    write32(NVMCTRL+NVMCTRL_CTRLB, (1 << 1)); /* 1 WS at 48MHz*/

    /* Reset SYSCTRL INT Status */
    write32(SYSCTRL+SYSCTRL_INTFLAG, 0xFFFFFFFF);

    /* Enable XOSC, with gain setting for a 16 MHz */
    reg =   (0x07 << 12) | /* Start-up delay */
            (0x03 << 8 ) | /* Gain setting   */
            (0x01 << 6)  | /* Ondemand*/
            (0x01 << 2 );  /* XTALEN */

    write32(SYSCTRL+SYSCTRL_XOSC, reg);

    reg |= (1 << 1); /* Enable oscillator */

    write32(SYSCTRL+SYSCTRL_XOSC, reg);


    /* Wait for oscillator ready */
    while (!(read32(SYSCTRL+SYSCTRL_PCLKSR) & 0x01));


    /* Disable DPLL */
    write32(SYSCTRL+SYSCTRL_DPLLCTRLA, 0);
    
    /**
     * fdpll96m_ref = f_xosc * ( 1 / (2 * (DIV + 1))) =
     *   =  16E6 * (1/(2*(7 + 1))) = 1 MHz
     *  DIV = 7
     */
    
    write32(SYSCTRL+SYSCTRL_DPLLCTRLB, (7 << 16) | /* DIV */
                                       (1 << 4));  /* Refclk = XOSC*/

    /**
     * fdpll96m = fdpll96m_ref * (LDR + 1 + LDFRAC/16) =
     *  = 1e6 * (47 + 1 + 0/16) = 48 MHz
     *
     */
    
    write32(SYSCTRL+SYSCTRL_DPLLRATIO, 47);

    /* Enable DPLL */

    write32(SYSCTRL+SYSCTRL_DPLLCTRLA, (1 << 6) | 2);

    /* Wait for PLL lock */

    while (read32(SYSCTRL+SYSCTRL_DPLLSTATUS) != 0x0F);

    
    write32(GCLK+GCLK_GENCTRL,  (1 << 16)   |
                                (0x08 << 8)); /* SRC = FDPLL96 */

    main();
    
    while (1);
}

__attribute__ ((section(".vectors")))
const void * exception_vectors[] = {
    (void *) &stack[__STACK_SIZE-1],
    (void *) &reset_handler,
    (void*) nmi_handler,
    (void*) hardfault_handler,
    (void*) (0ul), /* reserved */
    (void*) (0ul), /* reserved */
    (void*) (0ul), /* reserved */
    (void*) (0ul), /* reserved */
    (void*) (0ul), /* reserved */
    (void*) (0ul), /* reserved */
    (void*) (0ul), /* reserved */
    (void*) svc_handler,
    (void*) (0ul), /* reserved */
    (void*) (0ul), /* reserved */
    (void*) pendsv_handler,
    (void*) systick_handler,

    /* configurable interrupts */
    (void*) pm_handler,             /*  0 power manager */
    (void*) sysctrl_handler,        /*  1 system control */
    (void*) wdt_handler,            /*  2 watchdog timer */
    (void*) rtc_handler,            /*  3 real-time counter */
    (void*) eic_handler,            /*  4 external interrupt controller */
    (void*) nvmctrl_handler,        /*  5 non-volatile memory controller */
    (void*) dmac_handler,           /*  6 direct memory access controller */
    (void*) usb_handler,            /*  7 universal serial bus */
    (void*) evsys_handler,          /*  8 event system interface */
    (void*) sercom0_handler,        /*  9 serial communication interface 0 */
    (void*) sercom1_handler,        /* 10 serial communication interface 1 */
    (void*) sercom2_handler,        /* 11 serial communication interface 2 */
    (void*) sercom3_handler,        /* 12 serial communication interface 3 */
    (void*) sercom4_handler,        /* 13 serial communication interface 4 */
    (void*) sercom5_handler,        /* 14 serial communication interface 5 */
    (void*) tcc0_handler,           /* 15 timer counter control 0 */
    (void*) tcc1_handler,           /* 16 timer counter control 1 */
    (void*) tcc2_handler,           /* 17 timer counter control 2 */
    (void*) tc3_handler,            /* 18 basic timer counter 0 */
    (void*) tc4_handler,            /* 19 basic timer counter 1 */
    (void*) tc5_handler,            /* 20 basic timer counter 2 */
    (void*) tc6_handler,            /* 21 basic timer counter 3 */
    (void*) tc7_handler,            /* 22 basic timer counter 4 */
    (void*) adc_handler,            /* 23 analog digital converter */
    (void*) ac_handler,             /* 24 analog comparators */
    (void*) dac_handler,            /* 25 digital analog converter */
    (void*) ptc_handler,            /* 26 peripheral touch controller */
    (void*) i2s_handler             /* 27 inter-ic sound interface */
};
