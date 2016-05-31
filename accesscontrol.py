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

#GPIO constants
GREEN_LED = 11
YELLOW_LED = 12
RED_LED = 13
ORANGE_LED = 16
ENROL_BUTT = 15
RELAY = 18

filename = "userlist"

#loop boolean
continueLoop = True

#instantiate card reader
reader = MFRC522.MFRC522()

#instantiate file
#uidlist = open(filename, "a+", 1) #line buffered

#initialize GPIO
def initGPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ENROL_BUTT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(YELLOW_LED, GPIO.OUT)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setup(ORANGE_LED, GPIO.OUT)
    GPIO.setup(RELAY, GPIO.OUT)
            
#turn on a specific LED, turn others off
def selectLED(led):
    GPIO.setmode(GPIO.BOARD)
    GPIO.output(GREEN_LED, 0)
    GPIO.output(YELLOW_LED, 0)
    GPIO.output(RED_LED, 0)
    #GPIO.output(ORANGE_LED, 0)
    for i in range(0, len(led)):
        GPIO.output(led[i], 1)
    time.sleep(.01)

    
#handler function for signal.signal
def stopLoop(sig, frame):
    global continueLoop
    print "SIGINT captured, ending..."
    continueLoop = False

def uidToStr(uid):
    strOut = ""
    for i in range(len(uid)):
        strOut = strOut + str(hex(uid[i]))
    return strOut

def readCard():
    #Scan for Card
    global reader
    (status,TagType) = reader.MFRC522_Request(reader.PICC_REQALL)

    if status == reader.MI_OK:
        #print "Reading Card:"
        (status, uid) =  reader.MFRC522_Anticoll()
        if status ==reader.MI_OK:
            uidOut = uid[0:4]
            #print uidToStr(uidOut)
        else:
            selectLED([RED_LED])
            uidOut = [1, 0]
    else:
        selectLED([RED_LED])
        uidOut = [1, 1]
    
    #Adding this allows continuous reading without error
    (status,TagType) = reader.MFRC522_Request(reader.PICC_HALT)
    return uidOut
        

def main():
    global continueLoop
    global uidlist
    print "Starting..."
    #Check for SIGINT
    signal.signal(signal.SIGINT, stopLoop)
    #initialize GPIO
    initGPIO()
    selectLED([RED_LED])     

    while continueLoop:
        auth = False
        curUID = readCard()
        if GPIO.input(ENROL_BUTT):  #not enroling
            GPIO.output(ORANGE_LED, 0)
            if len(curUID) > 2:
                while True:
                    try:
                        uidlist = open(filename, "r") #line buffered
                        break
                    except IOError:
                        uidlist = open(filename, "a+")
                line = uidlist.readline()
                while line != "":
                    if  uidToStr(curUID) in line.strip():
                        selectLED([GREEN_LED])
                        auth = True
                        break
                    line = uidlist.readline()
                if line == "":
                    selectLED([YELLOW_LED])

        else:                       #enroling
            GPIO.output(ORANGE_LED, 1)
            if len(curUID) > 2:
                uidlist = open(filename, "a+", 1) #line buffered
                line = uidlist.readline()
                if line == "":
                    uidlist.write("Beginning of File: \n")
                    line = " "
                    
                while line != "":
                    if line.strip() == uidToStr(curUID):
                        #print "exists!"
                        break
                    line = uidlist.readline()
                    
                if line == "":
                    uidlist.write(uidToStr(curUID) + ", ")
                    GPIO.output(GREEN_LED, 1)
                    firstName = raw_input("New user's first name: ")
                    lastName = raw_input("New user's last name: ")
                    uidlist.write(firstName + ", " + lastName + "\n")
                    
                    time.sleep(1)
                uidlist.close()
        if auth:
            GPIO.output(RELAY, 0) #Relay ON
            #print "ON"
        else:
            GPIO.output(RELAY, 1) #Relay ON
            #print "OFF"
            


main()
GPIO.cleanup()

