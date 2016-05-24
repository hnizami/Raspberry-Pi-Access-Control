#!/usr/bin/python
##
##Name:       accesscontrol
##Purpose:    Read RFID card from RC522 module.
##
##Author:     Husain Nizami
##Created:    2016-05-24
##

import RPi.GPIO as GPIO
import MFRC522
import signal
import time

continueLoop = True

#handler function for signal.signal
def stopLoop(sig, frame):
    global continueLoop
    print "SIGINT captured, ending..."
    continueLoop = False
    GPIO.cleanup()

def main():
    global continueLoop
    print "Hello World"
    #Check for SIGINT
    signal.signal(signal.SIGINT, stopLoop)
    #instantiate card reader
    reader = MFRC522.MFRC522()

     

    while continueLoop:
        #Scan for Card
        (status,TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status ==reader.MI_OK:
            print "Card found"
            (status, uid) =  reader.MFRC522_Anticoll()
            print "UID: " + str(hex(uid[0]))+" "+str(hex(uid[1]))+" "+str(hex(uid[2]))+" "+str(hex(uid[3]))
            
main()
