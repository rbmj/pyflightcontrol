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
