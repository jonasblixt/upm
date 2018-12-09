#include <string.h>
#include <stdbool.h>
#include "samd21.h"
#include "usb.h"

#define USB_NO_EPS 8
#define USB_EP0_SIZE 64

static uint32_t base;
static struct usb_samd21_device_descriptor eps[USB_NO_EPS*2];
uint32_t ep0_buf_in[16] __attribute__((__aligned__(4)));
uint32_t ep0_buf_out[16] __attribute__((__aligned__(4)));
static uint16_t device_status;
uint32_t ep2_buf_out[16] __attribute__((__aligned__(4)));
uint32_t ep3_buf_in[16] __attribute__((__aligned__(4)));
static bool _enumerated = false;

static const uint8_t qf_descriptor[] = {
	0x0A,	//USB_DEV_QUALIFIER_DESC_LEN,
	0x06,   //USB_DEV_QUALIFIER_DESC_TYPE,
	0x00,   //USB_DEV_DESC_SPEC_LB,
	0x02,   //USB_DEV_DESC_SPEC_HB,
	0x00,   //USB_DEV_DESC_DEV_CLASS,
	0x00,   //USB_DEV_DESC_DEV_SUBCLASS,
	0x00,   //USB_DEV_DESC_DEV_PROTOCOL,
	0x40,   //USB_DEV_DESC_EP0_MAXPACKETSIZE,
	0x01,   //USB_DEV_DESC_NUM_OT_SPEED_CONF,
	0		//USB_DEV_DESC_RESERVED
};

/**
 *
 *  Endpoint 0 <--> USB Configuration endpoint
 *  Endpoint 2 <--> INTR OUT, used for commands from host -> device
 *  Endpoint 3 <--> INTR IN, used for responses from device -> host
 *
 */

static const struct usb_descriptors descriptors = {
    .device = {
        .bLength = 0x12, // length of this descriptor
        .bDescriptorType = 0x01, // Device descriptor
        .bcdUSB = 0x0200, // USB version 2.0
        .bDeviceClass = 0x00, // Device class (specified in interface descriptor)
        .bDeviceSubClass = 0x00, // Device Subclass (specified in interface descriptor)
        .bDeviceProtocol = 0x00, // Device Protocol (specified in interface descriptor)
        .bMaxPacketSize = 0x40, // Max packet size for control endpoint
        .idVendor = 0xffff, // Freescale Vendor ID. -- DO NOT USE IN A PRODUCT
        .idProduct = 0x0003, // Decvice ID -- DO NOT USE IN A PRODUCT
        .bcdDevice = 0x0000, // Device revsion
        .iManufacturer = 0x01, // Index of  Manufacturer string descriptor
        .iProduct = 0x01, // Index of Product string descriptor
        .iSerialNumber = 0x01, // Index of serial number string descriptor
        .bNumConfigurations = 0x01, // Number of configurations
    },
    .config = {
        .bLength = 0x09, //
        .bDescriptorType = 0x02, // Configuration descriptor
        .wTotalLength = 32,
        .bNumInterfaces = 0x01, // Number of interfaces
        .bConfigurationValue = 0x01, // Number to select for this configuration
        .iConfiguration = 0x00, // No string descriptor
        .bmAttributes = 0x80, // Self powered, No remote wakeup
        .MaxPower = 0xfa 
    },
    .interface = {
        .bLength = 0x09,
        .bDescriptorType = 0x04, // Interface descriptor
        .bInterfaceNumber = 0x00, // This interface = #0
        .bAlternateSetting = 0x00, // Alternate setting
        .bNumEndpoints = 0x02, // Number of endpoints for this interface
        .bInterfaceClass = 0xFF, 
        .bInterfaceSubClass = 0xFF,
        .bInterfaceProtocol = 0xFF, 
        .iInterface = 0, // No string descriptor
    },
    .endpoint_intr_out = {
        .bLength = 0x07,
        .bDescriptorType = 0x05, // Endpoint descriptor
        .bEndpointAddress = 0x02, 
        .bmAttributes = 0x3, 
        .wMaxPacketSize = 0x0040, 
        .bInterval = 0x05, 
    },
    .endpoint_intr_in = {
        .bLength = 0x07,
        .bDescriptorType = 0x05, // Endpoint descriptor
        .bEndpointAddress = 0x83, 
        .bmAttributes = 0x3, 
        .wMaxPacketSize = 0x0040, 
        .bInterval = 0x05,
    }
};

static const uint8_t usb_string_id[] = 
    {0x16,3,'U',0,'P',0,'M',0};


void usb_handler(void)
{
    while(1);
}

void usb_init(uint32_t _base)
{
    uint32_t caldata;
    base = _base;

    memset(eps, 0, USB_NO_EPS*sizeof(struct usb_samd21_device_descriptor));

    /* Reset USB */
    write8(base + USB_CTRLA, 1);
    while (read8(base + USB_SYNCBUSY) & 1);
    
    /* Enable */
    write8(base + USB_CTRLA, (1 << 1) | (1 << 2));
    while(read8(base + USB_SYNCBUSY) & 2);

    /**
     * Load calibration data from NVM
     *
     * Bit ranges adjusted to reflect that we start reading 32 bit's in.
     *
     * USB_TRANSN 17:13
     * USB_TRANSP 22:18
     * USB_TRIM   25:23
     *
     */
    caldata = read32(NVMCTRL_OTP4 + 0x04);

    uint8_t usb_cal_transn = (caldata >> 13) & 0x1F;
    uint8_t usb_cal_transp = (caldata >> 18) & 0x1F;
    uint8_t usb_cal_trim   = (caldata >> 23) & 0x07;

    write16(base + USB_PADCAL, (usb_cal_trim << 12)  |
                               (usb_cal_transn << 6) |
                               (usb_cal_transp));

    write32(base + USB_DESCADDR, (uint32_t) eps);

    write16(base + USB_INTFLAG, 0xffff);
    write16(base + USB_INTENSET, (1 << 3));
    write8(base + USB_DADD, (1 << 7));
    write16(base + USB_CTRLB, (1 << 9) |1);

    usb_reset();
}

void usb_reset(void)
{
    _enumerated = false;
    /* EP0 setup */
    eps[0].addr = (uint32_t) ep0_buf_out;
    eps[0].pcksize = (0x03 << 28);
    eps[1].addr = (uint32_t) ep0_buf_in;
    eps[1].pcksize = (0x03 << 28);

    write8(base + USB_EPINTENSET(0), (1 << 4));
    /* Configure EP0 in/out as Control in / Control setup, out */
    write8(base + USB_EPCFG(0), (1 << 4) | 1);
    //write8(base + USB_EPSTATUSCLR(0), (1 << 7) | (1 << 5) | (1 << 1) | 1);
    write8(base + USB_EPSTATUSCLR(0), 0xff);
    write8(base + USB_EPSTATUSSET(0), 1);
    write16(base + USB_CTRLB, 0);

    /* Configure EP2 & EP3 */

    eps[4].addr = (uint32_t) ep2_buf_out;
    eps[4].pcksize = (0x03 << 28);
    eps[7].addr = (uint32_t) ep3_buf_in;
    eps[7].pcksize = (0x03 << 28);

    write8(base + USB_EPCFG(2), 0x04);
    write8(base + USB_EPCFG(3), (0x04 << 4));

    write8(base + USB_EPSTATUSCLR(2), 0xff);
}

uint32_t usb_send_ep0(uint8_t *data, uint32_t sz)
{


    memcpy(ep0_buf_in, data, sz);
    eps[1].addr = (uint32_t) ep0_buf_in;
    eps[1].pcksize = (0x03 << 28) | sz;
    eps[1].extreg = 0;
    eps[1].status_bk = 0;

    write8(base + USB_EPINTFLAG(0), (1 << 1));
    write8(base + USB_EPSTATUSSET(0), (1 << 7));

    while ((read8(base + USB_EPINTFLAG(0)) & (1 << 1)) == 0);
    return 0;
}

uint32_t usb_send(uint8_t *data, uint32_t sz)
{
    memcpy(ep3_buf_in, data, sz);
    eps[7].addr = (uint32_t) ep3_buf_in;
    eps[7].pcksize = (0x03 << 28) | sz;
    eps[7].extreg = 0;
    eps[7].status_bk = 0;

    write8(base + USB_EPINTFLAG(3), (1 << 1));
    write8(base + USB_EPSTATUSSET(3), (1 << 7));

    while ((read8(base + USB_EPINTFLAG(3)) & (1 << 1)) == 0);
    return 0;
}

static void usb_enumerate(void)
{
    struct usb_setup_packet *setup = (struct usb_setup_packet*) ep0_buf_out;
    uint32_t sz;
    uint16_t request;

    request = (setup->bRequestType << 8) | setup->bRequest;
    
    switch (request) 
    {
        case USB_GET_DESCRIPTOR:
            if(setup->wValue == 0x0600) 
            {
                usb_send_ep0((uint8_t *) qf_descriptor, 
                                                    sizeof(qf_descriptor));
            } else if (setup->wValue == 0x0100) {
                
                sz = sizeof(struct usb_device_descriptor);

                if (setup->wLength <= sz)
                    sz = setup->wLength;
                

                usb_send_ep0((uint8_t *) &descriptors.device, sz);

            } else if (setup->wValue == 0x0200) {
                uint16_t desc_tot_sz = descriptors.config.wTotalLength;

                sz = desc_tot_sz;

                if (setup->wLength <= sz)
                    sz = setup->wLength;

                usb_send_ep0((uint8_t *) &descriptors.config, sz);
            } else if (setup->wValue == 0x0300) { 
                const uint8_t _usb_data[] = "\x04\x03\x04\x09";
                usb_send_ep0((uint8_t *) _usb_data, 4);
            } else if(setup->wValue == 0x0301) {
                
                sz = setup->wLength > sizeof(usb_string_id)?
                            sizeof(usb_string_id): setup->wLength;
                
                usb_send_ep0((uint8_t *) usb_string_id, sz);
     
            } else if (setup->wValue == 0x0A00) {
                uint16_t desc_tot_sz = descriptors.interface.bLength;

                sz = desc_tot_sz;

                if (setup->wLength < sz)
                    sz = setup->wLength;

                usb_send_ep0((uint8_t *) &descriptors.interface, sz);
                
            } else {
                while(1);
            }
        break;
        case USB_SET_ADDRESS:
        {
            uint8_t addr = setup->wValue & 0x7f;
            usb_send_ep0(NULL,0);
            write8(base + USB_DADD, (1 << 7) | addr);
        }
        break;
        case USB_SET_CONFIGURATION:
            _enumerated = true;
            usb_send_ep0(NULL, 0);
        break;
        case USB_SET_IDLE:
            usb_send_ep0(NULL,0);
        break;
        case USB_GET_STATUS:
            usb_send_ep0((uint8_t *) &device_status, 2);
            usb_send_ep0(NULL,0);
        break;
        default:
        break;
    }


}

bool usb_enumerated(void)
{
    return _enumerated;
}

bool usb_has_data(void)
{
    uint8_t ep2_int = read8(base + USB_EPINTFLAG(2));

    write8(base + USB_EPINTFLAG(2), ep2_int);
    return (ep2_int & 1);
}

uint8_t * usb_get_buf(void)
{

    write8(base + USB_EPSTATUSCLR(2), (1 << 6));
    return (uint8_t *) ep2_buf_out;
}

void usb_task(void)
{
    uint16_t status = read16(base + USB_INTFLAG);
    uint8_t ep0_int = read8(base + USB_EPINTFLAG(0));

    if (status & ( 1 << 3))
    {
        write16(base + USB_INTFLAG, (1 << 3));
        usb_reset();
    }

    /* Process setup packet on EP0 */
    if (ep0_int & (1 << 4))
    {
        write8(base + USB_EPINTFLAG(0), (1 << 4));
        write8(base + USB_EPSTATUSCLR(0), (1 << 6));
        usb_enumerate();
    }
    
    write16(base + USB_INTFLAG, status);
    write8(base + USB_EPINTFLAG(0), ep0_int);

}
