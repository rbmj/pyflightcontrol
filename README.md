pyflightcontrol
===============

License:  This project is licensed under the Apache License, version
2.0 (see LICENSE.md).  Font resources are included with the project
under the terms of the SIL Open Font License (see LICENSE.FONT.md).

Dependencies:

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
        python3-serial python3-pip
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

