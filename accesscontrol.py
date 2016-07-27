import RPi.GPIO as GPIO
import MFRC522
import signal
import time

#loop booleans
continueLoop = True

#GPIO constants
GREEN_LED = 13
YELLOW_LED = 12
RED_LED = 11
ORANGE_LED = 15
ENROL_BUTT = 16
RELAY = 18
BUZZER = 7

filename = "userlist"

#instantiate card reader
reader = MFRC522.MFRC522()

#initialize GPIO
def initGPIO():
    GPIO.setmode(GPIO.BOARD)
    #GPIO.setup(ENROL_BUTT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(YELLOW_LED, GPIO.OUT)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setup(ORANGE_LED, GPIO.OUT)
    GPIO.setup(RELAY, GPIO.OUT)
    GPIO.setup(BUZZER, GPIO.OUT)
            
#turn on a specific LED, turn others off
def selectLED(led):
    GPIO.output(GREEN_LED, 0)
    GPIO.output(YELLOW_LED, 0)
    GPIO.output(RED_LED, 0)
    GPIO.output(ORANGE_LED, 0)
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

def validateCard(curUID):
    uidlist = open(filename, "r")
    line = uidlist.readline()
    while line != "":                           #read until EOF
        if  curUID in line.strip():             #check for matching entry
            uidlist.close()
            selectLED([GREEN_LED])
            return True
        line = uidlist.readline()               #read next line
    uidlist.close()
    return False
    
def main():
    print "main"
    #loop booleans
    global continueLoop
    prevPresent = False
    auth = False
    #signal handler call
    signal.signal(signal.SIGINT, stopLoop)
    #initialize GPIO
    initGPIO()
    selectLED([RED_LED])
    GPIO.output(RELAY, 1)
    GPIO.output(BUZZER, 0)
    while True:
        try:
            uidlist = open(filename, "r") #line buffered
            break
        except IOError:
            uidlist = open(filename, "a+")
            uidlist.close()
    uidlist.close()
    while continueLoop:
        if prevPresent:
            UID = readCard()
            if len(UID) > 2:
                if auth:
                    if uidToStr(UID) in currUID:
                        auth = True
                    else:
                        auth = False
            else:
                if auth:
                    timeRemoved = time.time()
                    auth = False
                    prevPresent = False
                    timeElapsed = time.time() - timeRemoved
                    while (timeElapsed) <= 10:
                        UID = readCard()
                        if len(UID) > 2:
                            if uidToStr(UID) in currUID:
                                selectLED([GREEN_LED])
                                auth = True
                                prevPresent = True
                                break
                            else:
                                selectLED([RED_LED,ORANGE_LED])
                        if timeElapsed < 2:
                            GPIO.output(BUZZER, 1)
                        elif timeElapsed > 7:
                            if int(timeElapsed * 4) % 2 == 1:
                                GPIO.output(BUZZER, 0)
                            else:
                                GPIO.output(BUZZER, 1)
                        else:
                            GPIO.output(BUZZER, 0)
                        timeElapsed = time.time() - timeRemoved
                    GPIO.output(BUZZER, 0)
                    
                else:
                    prevPresent = False
        else:
            UID = readCard()
            if len(UID) > 2:
                currUID = uidToStr(UID)
                prevPresent = True
                if validateCard(currUID):
                    auth = True
                    selectLED([GREEN_LED])
                    time.sleep(2)
                    #print to log [084]
                else:
                    auth = False
                    selectLED([YELLOW_LED])
            else:
                print "no card"
                #no card
                
        if auth:
            GPIO.output(RELAY, 0) #Relay ON
            #print "ON"
        else:
            GPIO.output(RELAY, 1) #Relay OFF
            #print "OFF"

main()
GPIO.cleanup()
