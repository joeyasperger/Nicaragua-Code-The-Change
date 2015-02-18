import os
import glob
import time
import urllib
import urllib2
import time
import datetime
import RPi.GPIO as io
import json
io.setmode(io.BCM)
 
doorpin = 23
io.setup(doorpin, io.IN, pull_up_down=io.PUD_UP)

ipaddress = "169.254.10.73"

#sets up the raspberry pi to read the temperature input 
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')

#gets the file path to read the temperature from 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
#reads the raw temperature data from the file w1_slave 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#returns the value of the current temperature in celsius and fahrenheit 
def read_temp():
    lines = read_temp_raw() #gets raw file
    #strip away unnecessary parts of file to get temperature value
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        #convert temperature value to celsius and fahrenheit
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c
    
def detectDoor():
    if io.input(doorpin):
        return True
    else:
        return False 

while True:
    #reads temperature every second and sends to server
    try:
        temp_c = read_temp()
    except:
        print "unable to read temperature"
        temp_c = "nil"
    doorOpen = detectDoor()
    #reads current system time
    i = datetime.datetime.now() 
    timeString = i.isoformat()
    data = [{"temperature" : temp_c}, {"doorOpen" : doorOpen}, {"time" : timeString}]
    jsonString = json.dumps(data)
    print jsonString
    values = {"data" : jsonString}
    content = urllib.urlencode(values)
    url = 'http://%s:3000/new_reading/' % (ipaddress)
    req = urllib2.Request(url, content)
    try:  
        response = urllib2.urlopen(url, timeout = 5)
        html = response.read()
    except:
        print "HTTP request failed"
    time.sleep(5) #sleep until its time to take another temp reading
