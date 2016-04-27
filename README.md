pyflightcontrol
===============

Usage
---------------

Build/Install with (as root):

    # make install-{base,aircraft}

Aircraft services will start on boot.  All logs are passed to syslog
and can be directed by configuring your local syslog service.

To run the base station software, ensure that the flight controller is
connected to the computer, and run (as root):

    # python3 -m pyflightcontrol.base.base

Notes
----------------

License:  This project is licensed under the Apache License, version
2.0 (see LICENSE.md).  Font resources are included with the project
under the terms of the SIL Open Font License (see LICENSE.FONT.md).

Dependencies:  The below are the major dependencies - see below for a
complete list and installation instructions.

 - Python >= 3.4
 - Google Protocol Buffers & Python Bindings
 - pygame
 - pyusb
 - pyevdev

Random Notes/Gotchas:

 - The Maestro needs to be set up before use!
   - Go to Maestro Control Center
   - Enable all channels
   - Set serial mode to "USB Dual Port"
   - [IMPORTANT] Press "Apply Settings" in the lower right
 - Need to implement good error handling
   - Restart services if they die
   - Handle broken connections

GPS:
----------

GPSd doesn't autodetect these GPS chips, so you need to use
``gpsdctl add /dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A8008ZLA-if00-port0``
to add it.


XBee:
-------------

Getting the xbees to run low latency requires a bit of configuration in
XCTU.  The issue is that XBee tries to provide stream reliabilitly, and
pays a fairly steep performance penalty to do so.  This is usually OK,
but with a high frequency of traffic the latency combined with retransmits
causes the communications channel to get saturated.

Settings that need to get changed:
 - RR (Unicast Retries): 0
 - DH (Destination High): SH of peer
 - DL (Destination Low): SL of peer
 - TO (Transmit Options): C1
 - BD (Baud Rate): 115200

RPi Setup:
------------

In ``raspi-config``:
 - Expand Filesystem
 - Advanced Options -> SPI Enable
 - Advanced Options -> I2C Enable
 - Advanced Options -> Serial Disable
 - Exit and reboot

Run aptitude update && aptitude upgrade

Install Dependencies

[clone this repo]

Reconfigure network (/etc/network/interfaces):

    allow-hotplug eth0
    iface eth0 inet static
        address 172.16.0.2
        netmask 255.255.255.0
        gateway 172.16.0.1
        dns-nameservers 8.8.8.8

Connecting to RPi:
-------------------

SSH into the device, username pi password raspberry
Device is configured to be at IP 172.16.0.2/24 gateway 172.16.0.1
To connect to it, set your IP address to 172.16.0.1/24 on that interface

To allow internet traffic through your computer from the RPi, execute
the following on your machine, where ``<INET>`` is the interface with
internet access and ``<LAN>`` is the interface connected to the RPi:

    # sysctl -w net.ipv4.ip_forward=1
    # iptables -t nat -A POSTROUTING -o <INET> -j MASQUERADE
    # iptables -A FORWARD -i <INET> -o <LAN> -m state \
      --state RELATED,ESTABLISHED -j ACCEPT
    # iptables -A FORWARD -i <LAN> -o <INET> -j ACCEPT


Dependencies:
--------------

    $ sudo aptitude install python3 python3-dev python3-numpy git \
        python3-serial python3-pip protobuf-compiler
    $ sudo pip3 install pyusb --pre
    $ sudo aptitude install protobuf-compiler
    $ sudo pip3 install protobuf --pre
    ##### Only base station #####
    $ sudo aptitude install libav-tools libavcodec-dev libavformat-dev \
        libswscale-dev libportmidi-dev libsdl-{image,mixer}1.2-dev \
        libsdl-ttf2.0-dev libsdl1.2-dev mercurial
    $ sudo pip3 install hg+http://bitbucket.org/pygame/pygame
    $ sudo pip3 install evdev
    ##### Only Aircraft #####
    $ sudo aptitude install gpsd gpsd-clients python3-smbus
    $ PYTHON2=python`python --version 2>&1 | cut -d' ' -f2 | cut -d. -f1-2`
    $ PYTHON3=python`python --version 2>&1 | cut -d' ' -f2 | cut -d. -f1-2`
    $ sudo cp -r /usr/{lib/$PYTHON2,local/lib/$PYTHON3}/dist-packages/gps
    $ sudo 2to3 -w /usr/local/lib/$PYTHON3/dist-packages/gps
    $ sudo pip3 install wiringpi
    $ sudo pip3 install git+https://github.com/adafruit/Adafruit_Python_GPIO.git
    $ sudo pip3 install python-daemon

