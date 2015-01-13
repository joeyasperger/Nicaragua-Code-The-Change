import urllib2
response = urllib2.urlopen('http://google.com')
html = response.read()
print html