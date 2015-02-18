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

doorpin = 23
ipaddress = "169.254.10.73"

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

# returns whether the door is currently open or closed
def detectDoor():
    if io.input(doorpin):
        return True
    else:
        return False 

# sends an HTTP post request to the server containing the sensor data
def postToServer(connection, data):
    content = urllib.urlencode(data)
    headers = {}
    connection.request('POST', '/new_reading', content, headers)
    response = connection.getresponse()
    html = response.read()

def main():
    # set up for reading temperature sensor
    os.system('sudo modprobe w1-gpio')
    os.system('sudo modprobe w1-therm')

    #gets the file path to read the temperature from 
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
  
    # set up for reading door switch
    io.setmode(io.BCM)
    io.setup(doorpin, io.IN, pull_up_down=io.PUD_UP)

    connection = httplib.HTTPConnection('%s:3000' % (ipaddress))

    while True:
        #collects data and sends to server in loop
        try:
            temp_c = read_temp(device_file)
        except Exception as e:
            print "Unable to read temperature"
            print type(e)
            print e
            temp_c = "nil"
        doorOpen = detectDoor()
        currentTime = datetime.datetime.now() 
        timeString = currentTime.isoformat()
        data = [{"temperature" : temp_c}, {"doorOpen" : doorOpen}, {"time" : timeString}]
        jsonString = json.dumps(data)
        print jsonString
        values = {"data" : jsonString}
        postToServer(connection, values)
        time.sleep(5) #sleep until its time to take another temp reading

if __name__ == "__main__":
    main()
