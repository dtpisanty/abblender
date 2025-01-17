 ![abbblender](https://user-images.githubusercontent.com/57118670/129294809-657b26e4-5f12-424b-8db7-87c5726fe907.gif)
 
# abblender
ABBlender is a plugin for Blender 3D that allows animating ABB robots within Blender to be exported as RAPID modules (.mod files)
It has only been tested on 6-axis IRB-1600/10Kg/145 robots.

## Current Features
* Export rig positions as jointtarget
* Works with both forward-kinematic and reverse-kinematic rigs (look at the corresponding example blend files)
* Report current frame through TCP/IP messages for sync using native RAPID sockets (PC Interface must be enabled)
* RAPID tool name can be specified (default is tool0)

## Usage
Install like any add-on using the Blender Add-On installer (Preferences -> Add-ons). This will create a new tab on the sidebar (the one with view and tools) while in Object Mode, ABBlender is not available in any other mode.

### Bone naming
ABBlender works on rigged models of six axis robots. It's importat that the bones controlling each axis be named Axis1, Axis2, Axis3, Axis4, Axis5 and Axis6. In most situations you probably want a root bone as well. For inverse kinematics the control bone should be named IKcontrol.
(See example files robotControl.blend and robotControlIK.blend for details).

### Options
The ABBlender panel contains the settings used to export a RAPID .mod file that can be used in RobotStudio. The options are the following:
* Export Path: Directory in which the resulting file will be saved (default is the .blend files directory)
* Filename: The filename to use for exporting. This will also be the name of the module contained in the file so avoid RAPID command names.
* Step: The number of steps to skip before writting the next position. 1 will export all postions but will likely result in a "Too many close positions" error.
* Speed: The Tool Center Point speed in mm/seconds (This converts to vSpeed in RAPID code).
* Tool name: The tool used to drive the motion in RAPID
* Signal Name: Name of a digital output to drive (leave blank if no DO is meant to be used)
* Pulse signal: If enable pulses the previously defined signal using pulseDO
* Inverse Kinematiks: When checked bakes current IK before exporting.
* Report Frame: When the checkbox is enabled the program will send its current frame through TCP socket after every movement.
  * Host: IP address to report to
  * Port: Receiving port
* Export Joint Targets: Pressing this button will export the motion as a RAPID .mod file with the above parameters.

Once the file has been generated it's simply a matter of adding it to your controller in the RAPID tab in Robot Studio.

## Roadmap
1. Support for exporting robtargets
1. Integration with I/O board
1. Tool configuration
1. Collision detection
1. Tool path generation
1. Live robot motion from object mode

## Contact
Address any questions to dtrujillop@centro.edu.mx

## Credits
ABBlender is currently developed by Diego Trujillo-Pisanty at STEAM Lab within Centro de Diseño, Cine y Televisión in Mexico City
