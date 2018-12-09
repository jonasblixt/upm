
/**
 * UPM
 *
 * Copyright (C) 2018 Jonas Persson <jonpe960@gmail.com>
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
#ifndef __SAMD21_H__
#define __SAMD21_H__

#include <stdint.h>

static inline void write32(uint32_t reg, uint32_t val)
{
    *((volatile uint32_t *) reg) = val;
}

static inline uint32_t read32(uint32_t reg)
{
    return *((volatile uint32_t *)reg);
}


static inline void write16(uint32_t reg, uint16_t val)
{
    *((volatile uint16_t *) reg) = val;
}

static inline uint16_t read16(uint32_t reg)
{
    return *((volatile uint16_t *)reg);
}


static inline void write8(uint32_t reg, uint8_t val)
{
    *((volatile uint8_t *) reg) = val;
}

static inline uint8_t read8(uint32_t reg)
{
    return *((volatile uint8_t *)reg);
}

/* Cortex M0+ Registers */

#define SCS_BASE                       (0xE000E000)
#define SysTick_BASE        (SCS_BASE +  0x0010UL)                    /*!< SysTick Base Address */
#define NVIC_BASE           (SCS_BASE +  0x0100UL)                    /*!< NVIC Base Address */
#define SCB_BASE            (SCS_BASE +  0x0D00UL)                    /*!< System Control Block Base Address */

#define NVIC_ISER           (NVIC_BASE + 0x000)
#define NVIC_ICER           (NVIC_BASE + 0x080)
#define NVIC_ISPR           (NVIC_BASE + 0x100)
#define NVIC_ICPR           (NVIC_BASE + 0x180)
#define NVIC_IP             (NVIC_BASE + 0x300)

/* SAMD21 Registers */

#define AC                            (0x42004400) /**< \brief (AC) APB Base Address */
#define ADC                           (0x42004000) /**< \brief (ADC) APB Base Address */
#define DAC                           (0x42004800) /**< \brief (DAC) APB Base Address */
#define DMAC                          (0x41004800) /**< \brief (DMAC) APB Base Address */
#define DSU                           (0x41002000) /**< \brief (DSU) APB Base Address */
#define EIC                           (0x40001800) /**< \brief (EIC) APB Base Address */
#define EVSYS                         (0x42000400) /**< \brief (EVSYS) APB Base Address */
#define GCLK                          (0x40000C00) /**< \brief (GCLK) APB Base Address */
#define SBMATRIX                      (0x41007000) /**< \brief (SBMATRIX) APB Base Address */
#define I2S                           (0x42005000) /**< \brief (I2S) APB Base Address */
#define MTB                           (0x41006000) /**< \brief (MTB) APB Base Address */
#define NVMCTRL_AUX3                  (0x0080A000) /**< \brief (NVMCTRL) AUX3 Base Address */
#define NVMCTRL                       (0x41004000) /**< \brief (NVMCTRL) APB Base Address */
#define NVMCTRL_CAL                   (0x00800000) /**< \brief (NVMCTRL) CAL Base Address */
#define NVMCTRL_LOCKBIT               (0x00802000) /**< \brief (NVMCTRL) LOCKBIT Base Address */
#define NVMCTRL_OTP1                  (0x00806000) /**< \brief (NVMCTRL) OTP1 Base Address */
#define NVMCTRL_OTP2                  (0x00806008) /**< \brief (NVMCTRL) OTP2 Base Address */
#define NVMCTRL_OTP4                  (0x00806020) /**< \brief (NVMCTRL) OTP4 Base Address */
#define NVMCTRL_TEMP_LOG              (0x00806030) /**< \brief (NVMCTRL) TEMP_LOG Base Address */
#define NVMCTRL_USER                  (0x00804000) /**< \brief (NVMCTRL) USER Base Address */
#define PAC0                          (0x40000000) /**< \brief (PAC0) APB Base Address */
#define PAC1                          (0x41000000) /**< \brief (PAC1) APB Base Address */
#define PAC2                          (0x42000000) /**< \brief (PAC2) APB Base Address */
#define PM                            (0x40000400) /**< \brief (PM) APB Base Address */
#define PORT                          (0x41004400) /**< \brief (PORT) APB Base Address */
#define PORT_IOBUS                    (0x60000000) /**< \brief (PORT) IOBUS Base Address */
#define PTC                           (0x42004C00) /**< \brief (PTC) APB Base Address */
#define RTC                           (0x40001400) /**< \brief (RTC) APB Base Address */
#define SERCOM0                       (0x42000800) /**< \brief (SERCOM0) APB Base Address */
#define SERCOM1                       (0x42000C00) /**< \brief (SERCOM1) APB Base Address */
#define SERCOM2                       (0x42001000) /**< \brief (SERCOM2) APB Base Address */
#define SERCOM3                       (0x42001400) /**< \brief (SERCOM3) APB Base Address */
#define SYSCTRL                       (0x40000800) /**< \brief (SYSCTRL) APB Base Address */
#define TC3                           (0x42002C00) /**< \brief (TC3) APB Base Address */
#define TC4                           (0x42003000) /**< \brief (TC4) APB Base Address */
#define TC5                           (0x42003400) /**< \brief (TC5) APB Base Address */
#define TCC0                          (0x42002000) /**< \brief (TCC0) APB Base Address */
#define TCC1                          (0x42002400) /**< \brief (TCC1) APB Base Address */
#define TCC2                          (0x42002800) /**< \brief (TCC2) APB Base Address */
#define USB                           (0x41005000) /**< \brief (USB) APB Base Address */
#define WDT                           (0x40001000) /**< \brief (WDT) APB Base Address */

/* GCLK */

#define GCLK_CTRL            0x00
#define GCLK_STATUS          0x01
#define GCLK_CLKCTRL         0x02
#define GCLK_GENCTRL         0x04
#define GCLK_GENDIV          0x08

#define GCLK_ID_SERCOMx_SLOW 0x13
#define GCLK_ID_SERCOM1_CORE 0x15
#define GCLK_ID_USB          0x06

/* SYSCTRL */

#define SYSCTRL_XOSC         0x10
#define SYSCTRL_PCLKSR       0x0C
#define SYSCTRL_DPLLCTRLA    0x44
#define SYSCTRL_DPLLCTRLB    0x4C
#define SYSCTRL_DPLLRATIO    0x48
#define SYSCTRL_DPLLSTATUS   0x50
#define SYSCTRL_INTFLAG      0x08

/* NVMCTRL */

#define NVMCTRL_CTRLB        0x04

/* PORT */

#define PORT_DIRSET          0x08
#define PORT_DIRCLR          0x04
#define PORT_OUTSET          0x18
#define PORT_OUTCLR          0x14
#define PORT_WRCONFIG        0x28

#define PORT_PMUX0           0x30
#define PORT_PMUX1           0x31
#define PORT_PMUX2           0x32
#define PORT_PMUX3           0x33
#define PORT_PMUX4           0x34
#define PORT_PMUX5           0x35
#define PORT_PMUX6           0x36
#define PORT_PMUX7           0x37
#define PORT_PMUX8           0x38
#define PORT_PMUX9           0x39
#define PORT_PMUX10          0x3A
#define PORT_PMUX11          0x3B
#define PORT_PMUX12          0x3C
#define PORT_PMUX13          0x3D
#define PORT_PMUX14          0x3E
#define PORT_PMUX15          0x3F

#define MUX_A                0x00
#define MUX_B                0x01
#define MUX_C                0x02
#define MUX_D                0x03
#define MUX_E                0x04
#define MUX_F                0x05
#define MUX_G                0x06
#define MUX_H                0x07
#define MUX_I                0x08

#define PIN_PA0             (1 << 0)
#define PIN_PA1             (1 << 1)
#define PIN_PA2             (1 << 2)
#define PIN_PA3             (1 << 3)
#define PIN_PA4             (1 << 4)
#define PIN_PA5             (1 << 5)
#define PIN_PA6             (1 << 6)
#define PIN_PA7             (1 << 7)
#define PIN_PA8             (1 << 8)
#define PIN_PA9             (1 << 9)
#define PIN_PA10            (1 << 10)
#define PIN_PA11            (1 << 11)
#define PIN_PA14            (1 << 14)
#define PIN_PA15            (1 << 15)
#define PIN_PA16            (1 << 16)
#define PIN_PA17            (1 << 17)
#define PIN_PA18            (1 << 18)
#define PIN_PA19            (1 << 19)
#define PIN_PA22            (1 << 22)
#define PIN_PA23            (1 << 23)
#define PIN_PA24            (1 << 24)
#define PIN_PA25            (1 << 25)
#define PIN_PA27            (1 << 27)
#define PIN_PA28            (1 << 28)
#define PIN_PA30            (1 << 30)
#define PIN_PA31            (1 << 31)

#define SERCOM1_IRQn         10

/* PM */

#define PM_APBCMASK          0x20




#endif
