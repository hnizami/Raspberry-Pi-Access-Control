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

GREEN_LED = 11
YELLOW_LED = 12
RED_LED = 13

continueLoop = True

#initialize GPIO
def initGPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(YELLOW_LED, GPIO.OUT)
    GPIO.setup(RED_LED, GPIO.OUT)
    for i in range (GREEN_LED, RED_LED + 1):
        GPIO.output(i, 0)
        
#turn on a specific LED, turn others off
def selectLED(led):
    GPIO.setmode(GPIO.BOARD)
    for i in range (GREEN_LED, RED_LED + 1):
        #print "Setting GPIO: " + str(i)
        if i == led:
            GPIO.output(led, 1)
        else:
            GPIO.output(i, 0)
    

#handler function for signal.signal
def stopLoop(sig, frame):
    global continueLoop
    print "SIGINT captured, ending..."
    continueLoop = False

def main():
    global continueLoop
    print "Hello World"
    #Check for SIGINT
    signal.signal(signal.SIGINT, stopLoop)
    #instantiate card reader
    reader = MFRC522.MFRC522()
    #iinitialize GPIO
    initGPIO()
    selectLED(RED_LED)     

    while continueLoop:
        #Scan for Card
        (status,TagType) = reader.MFRC522_Request(reader.PICC_REQALL)
        if status ==reader.MI_OK:
            selectLED(YELLOW_LED)
            print "Card found"
        elif status == 1:
            selectLED(GREEN_LED)
        else:
            selectLED(RED_LED)
        
        (status, uid) =  reader.MFRC522_Anticoll()
        if status ==reader.MI_OK:
            print "UID: " + str(hex(uid[0]))+" "+str(hex(uid[1]))+" "+str(hex(uid[2]))+" "+str(hex(uid[3]))


main()
GPIO.cleanup()
