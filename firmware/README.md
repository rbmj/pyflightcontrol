AHRS Firmware
=========================

Prereqs: arduino-mk package
make, then make upload

Based on code from: http://github.com/ptrbrtzrazor-9dof-ahrs

Licensed under the GNU General Public License; see LICENSE

To read quaternion:
send "#oqb" for this output format
send "#sxy" to receive "#SYNCHxy" at a frame boundary
Frames will be a series of four byte floats:
 - e0
 - ex
 - ey
 - ez
 - accelx
 - accely
 - accelz
 - magx
 - magy
 - magz
 - gyrox
 - gyroy
 - gyroz

