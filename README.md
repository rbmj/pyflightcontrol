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

Dependencies:

    $ sudo aptitude install python3 python3-dev python3-numpy git \
        python3-serial
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
    $ sudo aptitude install gpsd gpsd-clients
    $ sudo cp -r /usr/{lib/python2.7,local/lib/python3.4}/dist-packages/gps
    $ sudo 2to3 -w /usr/local/lib/python3.4/dist-packages/gps
    $ sudo pip3 install wiringpi
