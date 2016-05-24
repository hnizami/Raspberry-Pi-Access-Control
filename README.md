# Raspberry-Pi-Access-Control

The Raspberry Pi will read a card, check if it is authorized, and release the 3D printer for use.

This code requires the SPI-Py extension installed from https://github.com/lthiery/SPI-Py.
The MFRC522.py class is the work of mxgxw from https://github.com/mxgxw/MFRC522-python.

Optional Hardware
Connect the cathode of the following LEDs to the respective GPIO pins:

Green LED 	pin 11
Yellow LED 	pin 12
Red LED		pin 13

connect the anode to ground using a 220 ohm resistor