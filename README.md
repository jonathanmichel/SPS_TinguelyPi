## Tinguely EV3 - *Tinguely Pi*

## Introduction

The **Tinguely EV3** project aims to provide a tangible interface that allows user to program EV3 devices with [Scratch blocks](https://scratch.mit.edu/ev3) in real life. It replaces [EV3 Classroom](https://education.lego.com/en-us/downloads/mindstorms-ev3/software#downloads) for educational purposes by empowering collaboration and learning by giving physical forms to digital information, thus taking advantage of the human ability to grasp and manipulate physical objects and materials. 

Blocks are physical devices containing an Arduino nano. They communicate each others on a serial line with magnetics connector in their notches. Each Scratch block has an unique ID and a pre-defined list of parameters. The lowest block sends its ID and parameters as a binary chain to the upper block. The later sends its ID and parameters with the data received from above. The uppermost block receives the full binary chain that represents the Scratch program and send it to a Raspberry Pi for decoding and generation of a MicroPython code that can be run on EV3 devices.   

**This repository contains the code that has to run on the Raspberry Pi**. It collects the binary chain transmitted through the blocks and convert it in a MicroPython code that uses the [pybricks](https://pybricks.com/ev3-micropython/index.html) library. It can also generate a visual representation of the code in ASCII.   

**For the code that has to be uploaded in the blocks (on Arduino), check the TinguelyBlock repository.**

A complete [User guide](https://hackmd.io/@jonathanmichel/B11DPn8wY) and [Developer guide](https://hackmd.io/@jonathanmichel/Hyz4LfKOF) (both in french) are available for additionnal information.


## Requirements
See [requirements.txt](requirements.txt)

## Code structure

Supported Scratch blocks are listed in [definitionAscii.xml](definitionAscii.xml). Each block has an unique ID and a pre-defined list of parameters.

For each block, an implementation has to be provided as described in [CodeImpl.py](CodeImplementations/CodeImpl.py). Currently, four implementations exist.   

- [GraphicCodeImpl](CodeImplementations/GraphicCodeImpl.py): Provides an ASCII visualisation of the code. Block drawing is handled by [AsciiDrawer.py](CodeImplementations/AsciiDrawer.py).

```
 ____________
/            \----------------------------------------------
| when program starts                                      |
|---    ----------------------------------------------------
|   \__/                                                   |
| if < (1) is pressed ? >                                  |
|   |---    ----------------------------------------------------
|   |   \__/                                                   |
|   | wait (5) seconds                                         |
|   |---    ----------------------------------------------------
|   |   \__/                                                   |
|   | set status light to [RED]                                |
|   ----    ------------------------------------------------
|       \__/                                               |
|                                                        ^ |
|___    ____________________________________________________
    \__/
```
- [PybricksCodeImpl](CodeImplementations/PybricksCodeImpl.py): Provides an implementation that uses the [pybricks](https://pybricks.com/ev3-micropython/index.html) library to program EV3 devices in MicroPython.

```
#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor, ColorSensor
from pybricks.parameters import *
from pybricks.tools import *

# Initialize the EV3 Brick.
ev3 = EV3Brick()

touch = TouchSensor(Port.S1)
booleanCheck = touch.pressed()
if booleanCheck:
    wait(5000)
    ev3.light.on(Color.RED)

```

- [Ev3DevPyhtonCodeImpl](CodeImplementations/Ev3DevPythonCodeImpl.py): Provides a implementation that uses the [ev3dev2](https://pypi.org/project/python-ev3dev2/) library to program EV3 devices in Python. **This implementation is deprecated because the library is to slow to import.** 

```python
# !/usr/bin/env python3
from time import time, sleep

from PIL import Image

from ev3dev2.display import Display
from ev3dev2.led import Leds
from ev3dev2.motor import Motor
from ev3dev2.sensor.lego import TouchSensor, UltrasonicSensor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4 

lcd = Display()

leds = Leds()

leds.all_off()

logo = Image.open('/home/robot/pics/EV3.bmp')
lcd.image.paste(logo, (0,0))
lcd.update()
# [h_on_start]
# <b_touch 1>
touch = TouchSensor(1)
booleanCheck = touch.is_pressed
if booleanCheck:
    sleep(5)
    leds.set_color('LEFT', 'RED')
	leds.set_color('RIGHT', 'RED')
```

- [PythonCodeImpl](CodeImplementations/PythonCodeImpl.py): Provides a pure Python implementation of the code. Used for debug purposes.

```python
# [h_on_start]
# <b_touch 1>
booleanCheck = False # b_touch 1
if booleanCheck: 
	time.sleep(5)
	print('Set color to RED')
```
 
The code implementation to use can simply be changed in [main.py](https://github.com/jonathanmichel/SPS_TinguelyPi/blob/3f8258f3b07d2a0a95b04eca9ee21b15a865daf3/main.py#L16). 

## Usage

Launch [main.py](main.py) to read serial line on `/dev/ttyUSB0` @ `9600Bds` and decode received binary chain.

A [SshHandler](SshHandler.py) allows then to send the generated python code to the EV3 brick running ev3dev. It provides functions to remotely launch and stop code execution. To do so, the EV3 device has to be connected to the Raspberry Pi, for example by USB as described [here](https://www.ev3dev.org/docs/tutorials/connecting-to-the-internet-via-usb/). See [config.ini](config.ini) for advanced configuration. Note that the current configuration uses passwordless authentification.  
 
## Authors

* **Jonathan Michel** - [jonathanmichel](https://github.com/jonathanmichel) 