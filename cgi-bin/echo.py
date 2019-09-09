#!/usr/bin/env python

import cgi

print "Content-Type: text/html\n\n"
print "<title>CGI Test</title>"
print "<html><body>"
The_Form = cgi.FieldStorage()
for name in The_Form.keys():
	print "Input: " + name + " Value: " + The_Form[name].value + "<BR>"

print "</body</html>"
