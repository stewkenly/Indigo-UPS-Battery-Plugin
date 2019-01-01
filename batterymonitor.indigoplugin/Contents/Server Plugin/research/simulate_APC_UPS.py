#! /usr/bin/env python
"""\
The purpose of this program is to simulate an APC UPS
It will respond to only 'basic' UPS commands
Presently only following commands are supported
YBFLOPR
"""
#
#	From http://karve.in/?p=269
#
import datetime
import serial
import glob
import sys
name="/dev/ttyUSB0" # change to suit your needs
ser = serial.Serial(name, 2400, timeout=1)
print "Trying to open" + name
if (ser.isOpen()) :
	print "Sucessfully opened port " + name
	print "Waiting for command on serial port"
	#loop start
	while 1	:
		timenow= datetime.datetime.now().strftime("%I:%M:%S") 
		cmd=ser.read() #read a single byte
		if len(cmd) != 0 :
			
			print timenow +  "--> Received command-> " + cmd
			#change output based on received command
			if cmd == 'Y':
				print timenow +  "--> Sending Reply SM"
				ser.write("SM\r\n")
			elif cmd == 'B':
				print timenow +  "--> Sending Reply 27.87"
				ser.write("27.87\r\n")
			elif cmd == 'F':
				print timenow +  "--> Sending Reply 50.00"
				ser.write("50.00\r\n")
			elif cmd == 'L':
				print timenow +  "--> Sending Reply 118.3"
				ser.write("118.3\r\n")
			elif cmd == 'O':
				print timenow +  "--> Sending Reply 118.3"
				ser.write("118.3\r\n")
			elif cmd == 'P':
				print timenow +  "--> Sending Reply 023.5"
				ser.write("023.5\r\n")
			elif cmd == 'f':
				print timenow +  "--> Sending Reply 099.0"
				ser.write("099.0\r\n")
			elif cmd == 'j':
				print timenow +  "--> Sending Reply 00327:"
				ser.write("0327:")
			elif cmd == 'R':
				print timenow +  "--> Sending Reply BYE"
				ser.write("BYE\r\n")
			print "-----------------------------------------------------"
		
		
	ser.close()