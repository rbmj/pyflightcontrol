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

    allow-hotplug eth0
    iface eth0 inet static
        address 172.16.0.2
        netmask 255.255.255.0
        gateway 172.16.0.1

Connecting to RPi:
-------------------

SSH into the device, username pi password raspberry
Device is configured to be at IP 172.16.0.2/24 gateway 172.16.0.1
To connect to it, set your IP address to 172.16.0.1/24 on that interface
To allow internet traffic through your computer from the RPi, execute
the following on your machine:

    sysctl -w net.ipv4.ip_forward=1

Install dependencies.


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

