import urllib2
import urllib

url = 'http://169.254.119.4:3000/new_reading?temp=231&time=1123'
#values = {'temp' : '20.3',
 #         'time' : '11:21'}

#data = urllib.urlencode(values)
#req = urllib2.Request(url, data)
req = url
response = urllib2.urlopen(req)
html = response.read()
print html
