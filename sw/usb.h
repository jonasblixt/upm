#ifndef __USB_H__
#define __USB_H__

#include <stdint.h>
#include <stdbool.h>

/* Standard USB structures */

struct usb_setup_packet {
    uint8_t bRequestType;	   // Characteristics of request 
    uint8_t bRequest;           // Specific request
    uint16_t wValue;            // Word-sized field that varies according to request
    uint16_t wIndex;            // Index
    uint16_t wLength;           // Number of bytes to transfer
}  __attribute__ ((packed));

struct usb_device_descriptor {
    uint8_t bLength;		       // Size of this descriptor in bytes
    uint8_t bDescriptorType;	   // DEVICE Descriptor Type
    uint16_t bcdUSB;		       // USB Specification Release Number
    uint8_t bDeviceClass;	   // Class code
    uint8_t bDeviceSubClass;	   // Subclass code
    uint8_t bDeviceProtocol;	   // Protocol code
    uint8_t bMaxPacketSize;	   // Maximum packet size for endpoint zero
    uint16_t idVendor;          // Vendor ID
    uint16_t idProduct;         // Product ID
    uint16_t bcdDevice;         // Device release number
    uint8_t iManufacturer;      // Index of string descriptor describing manufacturer
    uint8_t iProduct;           // Index of string descriptor describing product
    uint8_t iSerialNumber; 	   // Index of string descriptor describing the device's serial number
    uint8_t bNumConfigurations; // Number of possible configurations
}  __attribute__ ((packed));

struct usb_configuration_descriptor {
    uint8_t bLength;			    // Size of descriptor	
    uint8_t bDescriptorType;		// CONFIGURATION Descriptor Type
    uint16_t wTotalLength;       // Total length of data returned for this configuration
    uint8_t bNumInterfaces;      // Number of interfaces supported by this configuration
    uint8_t bConfigurationValue; // Value to use as an argument to the to select this configuration
    uint8_t iConfiguration;      // Index of string descriptor describing this configuration
    uint8_t bmAttributes;		// Configuration characteristics
    uint8_t MaxPower;			// Maximum power consumption of the USB device
}  __attribute__ ((packed));

struct usb_interface_descriptor {
    uint8_t bLength;		       // Size of this descriptor in bytes 
    uint8_t bDescriptorType;    // INTERFACE Descriptor Type
    uint8_t bInterfaceNumber;   // Number of this interface
    uint8_t bAlternateSetting;  // Value used to select this alternate setting
    uint8_t bNumEndpoints;      // Number of endpoints used by this interface
    uint8_t bInterfaceClass;    // Class code
    uint8_t bInterfaceSubClass; // Subclass code
    uint8_t bInterfaceProtocol; // Protocol code
    uint8_t iInterface;		   // Index of string descriptor describing this interface
}  __attribute__ ((packed));


struct usb_endpoint_descriptor {
    uint8_t bLength;		       // Size of this descriptor in bytes 
    uint8_t bDescriptorType;    // ENDPOINT Descriptor Type
    uint8_t bEndpointAddress;   // The address of the endpoint on the USB device described by this descriptor
    uint8_t bmAttributes;       // The endpoint'ss attributes
    uint16_t wMaxPacketSize;    //  Maximum packet size
    uint8_t bInterval;          // Interval for polling endpoint for data transfers
}  __attribute__ ((packed));


struct usb_descriptors {
    const struct usb_device_descriptor device;
    const struct usb_configuration_descriptor config;
    const struct usb_interface_descriptor interface;
    const struct usb_endpoint_descriptor endpoint_intr_out;
    const struct usb_endpoint_descriptor endpoint_intr_in;
} __attribute__ ((packed));

/* Defines for commands in setup packets */
#define USB_GET_DESCRIPTOR				0x8006
#define USB_SET_CONFIGURATION			0x0009
#define USB_SET_IDLE					0x210A
#define USB_SET_FEATURE					0x0003
#define USB_SET_ADDRESS                 0x0005
#define USB_GET_STATUS                  0x8000




/* SAMD21 Specific structures */

struct usb_samd21_device_descriptor {
    uint32_t addr;
    uint32_t pcksize;
    uint16_t extreg;
    uint8_t status_bk;
    uint8_t __rz[0x05];
} __attribute__((packed));


/* USB Device register offset's */

#define USB_CTRLA            0x00
#define USB_SYNCBUSY         0x02
#define USB_QOSCTRL          0x03
#define USB_FSMSTATUS        0x0D
#define USB_DESCADDR         0x24
#define USB_PADCAL           0x28
#define USB_CTRLB            0x08
#define USB_DADD             0x0A
#define USB_STATUS           0x0C
#define USB_FNUM             0x10
#define USB_INTENCLR         0x14
#define USB_INTENSET         0x18
#define USB_INTFLAG          0x1C
#define USB_EPINTSMRY        0x20

#define USB_EPCFG(n)         (0x100+n*0x20)
#define USB_EPSTATUSCLR(n)   (0x104+n*0x20)
#define USB_EPSTATUSSET(n)   (0x105+n*0x20)
#define USB_EPSTATUS(n)      (0x106+n*0x20)
#define USB_EPINTFLAG(n)     (0x107+n*0x20)
#define USB_EPINTENCLR(n)    (0x108+n*0x20)
#define USB_EPINTENSET(n)    (0x109+n*0x20)



void usb_init(uint32_t _base);
void usb_task(void);
void usb_reset(void);
uint32_t usb_send(uint8_t *data, uint32_t sz);
bool usb_enumerated(void);

uint8_t * usb_get_buf(void);
bool usb_has_data(void);
#endif
