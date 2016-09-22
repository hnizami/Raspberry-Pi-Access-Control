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

filepath = "/home/pi/RFID/Raspberry-Pi-Access-Control/"
filename = filepath + "userlist"
logname = filepath + "usage.log"
beatname = filepath + "heartbeat.log"

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
    #print "main"
    #loop booleans
    global continueLoop
    prevPresent = False
    auth = False
    present = False
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

#logfile
    logfile = open(logname, "a+", 1)
    line = logfile.readline()
    if line =="":
        logfile.write("Start of log:\n")
        line = " "
    while line != "":
        line = logfile.readline()
    logfile.write("\nAccesscontrol Started: "+ time.strftime("%Y-%m-%d, %H:%M:%S") + "\n")

#heartbeat
    heartfile = open(beatname, "a+", 1)
    lastbeat = time.time()
    heartfile.write(time.strftime("%Y-%m-%d, %H:%M:%S")+"\n")


    while continueLoop:
        if prevPresent:
            UID = readCard()
            if len(UID) > 2:    #card present
                if auth:
                    if uidToStr(UID) in currUID:
                        present = True
                        auth = True
                    else:
                        present = False
                        auth = False
            else:               #card absent
                if auth:
                    timeRemoved = time.time()
                    auth = False
                    present = False
                    timeElapsed = time.time() - timeRemoved
                    while (timeElapsed) <= 10:
                        UID = readCard()
                        if len(UID) > 2:
                            if uidToStr(UID) in currUID: #correct card
                                selectLED([GREEN_LED])
                                auth = True
                                present = True
                                break
                            else:                       #incorrect card
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
                    present = False
        else:   #Prev Absent
            UID = readCard()
            if len(UID) > 2: #currently present
                currUID = uidToStr(UID)
                present = True
                if validateCard(currUID):   #valid card
                    auth = True
                    selectLED([GREEN_LED])
                    time.sleep(0.25)
                    #print to log [084]
                else:                       #invalid card
                    auth = False
                    selectLED([YELLOW_LED])
            #else:
                #print "no card"
                #no card
        if prevPresent != present:
            if auth:
                GPIO.output(RELAY, 0) #Relay ON
                logfile.write("Printer Started: "+ time.strftime("%Y-%m-%d, %H:%M:%S"))
                #print "ON"
            else:
                GPIO.output(RELAY, 1) #Relay OFF
                logfile.write(", Printer Stopped: "+ time.strftime("%Y-%m-%d, %H:%M:%S") + "\n")
                #print "OFF"
            prevPresent = present
        time.sleep(.1)
        if (time.time() - lastbeat > 59.5):
            lastbeat = time.time()
            heartfile.write(time.strftime("%Y-%m-%d, %H:%M:%S")+"\n")
    logfile.close()
    heartfile.close()
main()
GPIO.cleanup()

