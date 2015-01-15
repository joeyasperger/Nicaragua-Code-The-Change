import os
import glob
import time
import urllib
import urllib2
import time
import datetime

 
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    
while True:
    temp_c, temp_f = read_temp()
    print temp_c
    i = datetime.datetime.now()
    url = 'http://169.254.119.4:3000/new_reading?temp=%f&time=%s' % (temp_c, i.isoformat())
    response = urllib2.urlopen(url)
    html = response.read()
    time.sleep(1)
