/**
 * UPM cli
 *
 * Copyright (C) 2018 Jonas Persson <jonpe960@gmail.com>
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */

#include <sys/stat.h>
#include <unistd.h>
#include <ctype.h>
#include <stdlib.h>
#include <sys/types.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <libusb-1.0/libusb.h>
#include <uuid/uuid.h>
#include <string.h>
#include <ncurses.h>

#include "protocol.h"

static libusb_context *ctx = NULL;

static libusb_device * find_device(libusb_device **devs)
{
	libusb_device *dev;
	int i = 0;

	while ((dev = devs[i++]) != NULL) {
		struct libusb_device_descriptor desc;
		int r = libusb_get_device_descriptor(dev, &desc);
		if (r < 0) {
			return NULL;
		}

        if ( (desc.idVendor == 0xffff) && (desc.idProduct == 0x0003)) {
            return dev;
        }
		
	}

    return NULL;
}


#define CTRL_IN			LIBUSB_ENDPOINT_IN |LIBUSB_REQUEST_TYPE_CLASS|LIBUSB_RECIPIENT_INTERFACE
#define CTRL_OUT		LIBUSB_ENDPOINT_OUT|LIBUSB_REQUEST_TYPE_CLASS|LIBUSB_RECIPIENT_INTERFACE

float raw2mWh(uint8_t *in)
{
    uint64_t d = 0;
    memcpy(&d, in, 6);

    float mWh = (float) d / 0x10000000;
    mWh *= 32.0;
    mWh /= 1024;
    mWh *= 1/3.6 * 100;

    return mWh;
}

int main(int argc, char **argv) {
    libusb_device_handle *h;
	libusb_device **devs;
    libusb_device *dev;
	int r;
	ssize_t cnt;
    int err;


	r = libusb_init(&ctx);
	if (r < 0)
		return r;


	cnt = libusb_get_device_list(NULL, &devs);
	if (cnt < 0)
		return (int) cnt;

	dev = find_device(devs);
	libusb_free_device_list(devs, 1);

    if (dev == NULL) {
        printf ("Could not find device\n\r");
        libusb_exit (NULL);
        return -1;
    }


    h = libusb_open_device_with_vid_pid(ctx, 0xffff, 0x0003);

    if (libusb_kernel_driver_active(h, 0))
		 libusb_detach_kernel_driver(h, 0);

    err = libusb_claim_interface(h, 0);
    
    if (err != 0) {
        printf ("Claim interface failed (%i)\n", err);
        return -1;
    }

    if (h == NULL) {
        printf ("Could not open device\n");
        return -1;
    }

    //upm_write(h,0,0,0);

    WINDOW *w = initscr();
    cbreak();
    nodelay(w, true);
    noecho();
    curs_set(0);

    bool flag_run = true;
    uint32_t i = 0;
    struct upm_in in;
    struct upm_out out;
    int rx_sz;

    memset(&out, 0, sizeof(struct upm_out));

    while(flag_run)
    {
        char c = getch();

        err = libusb_interrupt_transfer(h,
                    LIBUSB_ENDPOINT_IN|3,
                    (uint8_t *) &in, sizeof (struct upm_in) , &rx_sz, 10000);

        if (err < 0) {
            clear();
            refresh();
            endwin();

            printf ("upm_read: %i %i\n", err,rx_sz);
            goto err_out;
        }

        if (c == 'q')
            break;

        if (c == 'A')
            out.outputs_set = (1 << 0);
        if (c == 'a')
            out.outputs_clr = (1 << 0);

        if (c == 'S')
            out.outputs_set = (1 << 1);
        if (c == 's')
            out.outputs_clr = (1 << 1);

        if (c == 'D')
            out.outputs_set = (1 << 2);
        if (c == 'd')
            out.outputs_clr = (1 << 2);

        if (c == 'F')
            out.outputs_set = (1 << 3);
        if (c == 'f')
            out.outputs_clr = (1 << 3);

        if (c == 'r')
            out.counter_reset = (1 << 0);

        err = libusb_interrupt_transfer(h,
                    0x02,
                    (uint8_t *) &out, sizeof (struct upm_out) , &rx_sz, 10000);

        if (err < 0) {
            clear();
            refresh();
            endwin();

            printf ("upm_write: %i %i\n", err,rx_sz);
            goto err_out;
        }
    
        out.outputs_set = 0;
        out.outputs_clr = 0;
        out.counter_reset = 0;

        float V_usb = (float) in.Vbus[0]/0xFFFF * 32.0;
        float I_usb = (float) in.Vsns[0]/0xFFFF * 1000.0;
        float mWh_usb = raw2mWh(in.Ereg[0]);

        float V_in1 = (float) in.Vbus[1]/0xFFFF * 32.0;
        float I_in1 = (float) in.Vsns[1]/0xFFFF * 1000.0;
        float mWh_in1 = raw2mWh(in.Ereg[1]);


        float V_in2 = (float) in.Vbus[2]/0xFFFF * 32.0;
        float I_in2 = (float) in.Vsns[2]/0xFFFF * 1000.0;
        float mWh_in2 = raw2mWh(in.Ereg[2]);

        float V_in3 = (float) in.Vbus[3]/0xFFFF * 32.0;
        float I_in3 = (float) in.Vsns[3]/0xFFFF * 1000.0;
        float mWh_in3 = raw2mWh(in.Ereg[3]);

        i = i + 1;
        mvwprintw(w, 0, 0, "0 USB %6.3f V, %7.2f mA, %6.1f mWh | Out 0 : %s",
                            V_usb,I_usb,mWh_usb,in.outputs & (1 << 0)?"ON ":"OFF");
        mvwprintw(w, 1, 0, "1 IN1 %6.3f V, %7.2f mA, %6.1f mWh | Out 1 : %s",
                            V_in1,I_in1,mWh_in1,in.outputs & (1 << 1)?"ON ":"OFF");
        mvwprintw(w, 2, 0, "2 IN2 %6.3f V, %7.2f mA, %6.1f mWh | Out 2 : %s",
                            V_in2,I_in2,mWh_in2,in.outputs & (1 << 2)?"ON ":"OFF");
        mvwprintw(w, 3, 0, "3 IN3 %6.3f V, %7.2f mA, %6.1f mWh | Out 3 : %s",
                            V_in3,I_in3,mWh_in3,in.outputs & (1 << 3)?"ON ":"OFF");

    }

    clear();
    refresh();
    endwin();
err_out:
    libusb_exit(NULL);
	return 0;
}
