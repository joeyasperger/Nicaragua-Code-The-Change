import os
import glob
import time
import urllib
import urllib2
import httplib
import time
import datetime
import RPi.GPIO as io
import json
import sys
import Adafruit_DHT

DHTpin = 4
doorpin = 23
ipaddress = "169.254.209.41"

#reads the raw temperature data from the file w1_slave 
def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#returns the value of the current temperature in celsius and fahrenheit 
def read_temp(device_file):
    lines = read_temp_raw(device_file) #gets raw file
    #strip away unnecessary parts of file to get temperature value
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        #convert temperature value to celsius and fahrenheit
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

# returns true if the door is open
def detectDoor():
    if io.input(doorpin):
        return True
    else:
        return False 

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
  return cpuserial

# sends an HTTP post request to the server containing the sensor data
def postToServer(connection, data):
    content = urllib.urlencode(data)
    headers = {}
    connection.request('POST', '/new_reading', content, headers)
    response = connection.getresponse()
    html = response.read()

# monitors when the door is opened and returns array of time and duration of each opening
# runs for the time passed in seconds
def getDoorData(timeInterval):
    doorData = []
    doorWasOpen = False
    duration = 0
    for i in range(1,timeInterval):
        currentState = detectDoor()
        if currentState:
            if doorWasOpen:
                duration += 1
            else:
                startTime = datetime.datetime.now()
        else:
            if doorWasOpen:
                duration += 1
                data = {"timeOpened" : startTime.isoformat(), "duration" : duration}
                doorData.append(data)
                duration = 0
        doorWasOpen = currentState
        time.sleep(1)
    return doorData

def main():
    # set up for reading door switch
    io.setmode(io.BCM)
    io.setup(doorpin, io.IN, pull_up_down=io.PUD_UP)

    connection = httplib.HTTPConnection('%s:3000' % (ipaddress))

    while True:
        #collects data and sends to server in loop
        doorData = getDoorData(30)
        print doorData
        try:
            humidity, temperature = Adafruit_DHT.read_retry(22, DHTpin)
        except Exception as e:
            print "Unable to read temperature"
            print type(e)
            print e
            temp_c = "nil"
        currentTime = datetime.datetime.now() 
        timeString = currentTime.isoformat()
        serial = getserial()
        data = [{"serial number" : serial}, {"temperature" : temperature}, {"doorData" : doorData}, {"time" : timeString}, {"humidity" : humidity}]
        jsonString = json.dumps(data)
        print jsonString
        values = {"data" : jsonString}
        postToServer(connection, values)

if __name__ == "__main__":
    main()
