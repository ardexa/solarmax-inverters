#! /usr/bin/python

# Copyright (c) 2013-2017 Ardexa Pty Ltd
#
# This code is licensed under the MIT License (MIT).
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

# This script will query a Solarmax inverter. Usage: python solarmax-ardexa.py {serial device} {Start Address} {End Address} {log directory} {Comma separated list of values}, where...
# {serial device} = ..something lie: /dev/ttyS0
# {Start Address} = start range 1-32 of the RS485 address
# {End Address} = end range 1-32 of the RS485 address
# {log directory} = logging directory
# {Comma separated list of values} = list of "query_dict" values below as a single string with no spaces, like: KDY,IL1,IL2,IL3,PAC,PDC,TNF,TKK,SYS,KHR,KMT,KLM,UL1,UL2,UL3,PRL
# eg: python solarmax-ardexa.py /dev/ttyS0 1 5 /opt/ardexa/solarmax/logs KDY,IL1,IL2,IL3,PAC,PDC,TNF,TKK,SYS,KHR,KMT,KLM,UL1,UL2,UL3,PRL
# eg; ./solarmax-ardexa.py /dev/ttyS0 1 5 /opt/ardexa/solarmax/logs KDY,IL1,IL2,IL3,PAC,PDC,TNF,TKK,SYS,KHR,KMT,KLM,UL1,UL2,UL3,PRL
#
# For use on Linux systems
# Make sure the following tools have been installed
#		sudo apt-get install python-pip
#		sudo pip install pyserial
#

import serial
import sys
import time
import os
from Supporting import *

# Change these 3 settings to suit your installation, if required
DEBUG = 0
#####################REQUIRED_VALUES = ['KDY','IL1','IL2','IL3','PAC','PDC','TNF','TKK','SYS','KHR', 'KMT', 'KLM', 'UL1', 'UL2', 'UL3', 'PRL']

PIDFILE = 'solarmax-ardexa.pid'
USAGE = "python solarmax-ardexa.py {serial device} {start address} {end address} {log directory} {Comma separated list of values} eg; python solarmax-ardexa.py /dev/ttyS1 1 13 /opt/ardexa/solarmax KDY,IL1,IL2,IL3,PAC,PDC,TNF,TKK,SYS,KHR,KMT,KLM,UL1,UL2,UL3,PRL"

query_dict = {	'KDY' : 'Energy today (Wh)', 'KDL' : 'Energy yesterday (Wh)', 'KYR' : 'Energy this year (kWh)', 'KLY' : 'Energy last year (kWh)',
					'KMT' : 'Energy this month (kWh)', 'KLM' : 'Energy last month (kWh)', 'KT0' : 'Total Energy(kWh)', 'IL1' : 'AC Current Phase 1 (A)' , 
					'IL2' : 'AC Current Phase 2 (A)', 'IL3' : 'AC Current Phase 3 (A)', 'IDC' : 'DC Current (A)', 'PAC' : 'AC Power (W)',
					'PDC' : 'DC Power (W)', 'PRL' : 'Relative power (%)', 'TNP' : 'Grid period duration',	
					'TNF' : 'Generated Frequency (Hz)', 'TKK' : 'Inverter Temperature (C)', 'UL1' : 'AC Voltage Phase 1 (V)', 
					'UL2' : 'AC Voltage Phase 2 (V)', 'UL3' : 'AC Voltage Phase 3 (V)', 'UDC' : 'DC Voltage (V)',
					'ADR' : 'Address', 'TYP' : 'Type', 'PIN' : 'Installed Power (W)', 'CAC' : 'Start Ups (?)', 'KHR' : 'Operating Hours', 
					'SWV' : 'Software Version', 'DDY' : 'Date day', 'DMT' : 'Date month', 'DYR' : 'Date year', 'THR' : 'Time hours',
					'TMI' : 'Time minutes',	'LAN' : 'Language', 
					'SAL' : 'System Alarms', 'SYS' : 'System Status',   
					'MAC' : 'MAC Address', 'EC00' : 'Error Code 0', 'EC01' : 'Error Code 1', 'EC02' : 'Error Code 2', 'EC03' : 'Error Code 3', 
					'EC04' : 'Error Code 4', 'EC05' : 'Error Code 5', 'EC06' : 'Error Code 6', 'EC07' : 'Error Code 7', 'EC08' : 'Error Code 8',
					'BDN' : 'Build number', 
					'DIN' : '?',  
					'SDAT' : 'datetime ?', 'FDAT' : 'datetime ?', 
					'U_AC' : '?', 'F_AC' : 'Grid Frequency', 'SE1': '', 
					'U_L1L2' : 'Phase1 to Phase2 Voltage (V)', 'U_L2L3' : 'Phase2 to Phase3 Voltage (V)', 'U_L3L1' : 'Phase3 to Phase1 Voltage (V)'
}

alarm_codes = {
          0: 'No Error',
          1: 'External Fault 1',
          2: 'Insulation fault DC side',
          4: 'Earth fault current too large',
          8: 'Fuse failure midpoint Earth',
         16: 'External alarm 2',
         32: 'Long-term temperature limit',
         64: 'Error AC supply ',
        128: 'External alarm 4',
        256: 'Fan failure',
        512: 'Fuse failure ',
       1024: 'Failure temperature sensor',
       2048: 'Alarm 12',
       4096: 'Alarm 13',
       8192: 'Alarm 14',
      16384: 'Alarm 15',
      32768: 'Alarm 16',
      65536: 'Alarm 17',
  }

# These are directly from the maxmonitoring downloads EN localisation file
status_codes = {
		20001 : 'Running', 20002 : 'Irradiance too low', 20003 : 'Startup', 20004 : 'MPP operation', 20006 : 'Maximum power',
		20007 : 'Temperature limitation', 20008 : 'Mains operation', 20009 : 'Idc limitation', 20010 : 'Iac limitation',
		20011 : 'Test mode', 20012 : 'Remote controlled', 20013 : 'Restart delay', 20014 : 'External limitation',
		20015 : 'Frequency limitation', 20016 : 'Restart limitation', 20017 : 'Booting', 20018 : 'Insufficient boot power',
		20019 : 'Insufficient power', 20021 : 'Uninitialized', 20022 : 'Disabled', 20023 : 'Idle', 20024 : 'Powerunit not ready',
		20050 : 'Program firmware', 20101 : 'Device error 101', 20102 : 'Device error 102', 20103 : 'Device error 103',
		20104 : 'Device error 104', 20105 : 'Insulation fault DC', 20106 : 'Insulation fault DC', 20107 : 'Device error 107', 
		20108 : 'Device error 108', 20109 : 'Vdc too high', 20110 : 'Device error 110', 20111 : 'Device error 111', 20112 : 'Device error 112', 
		20113 : 'Device error 113', 20114 : 'Ierr too high', 20115 : 'No mains', 20116 : 'Frequency too high', 20117 : 'Frequency too low', 
		20118 : 'Mains error', 20119 : 'Vac 10min too high', 20120 : 'Device error 120', 20121 : 'Device error 121', 20122 : 'Vac too high', 
		20123 : 'Vac too low', 20124 : 'Device error 124', 20125 : 'Device error 125', 20126 : 'Error ext. input 1', 20127 : 'Fault ext. input 2', 
		20128 : 'Device error 128', 20129 : 'Incorr. rotation dir.', 20130 : 'Device error 130', 20131 : 'Main switch off', 20132 : 'Device error 132', 
		20133 : 'Device error 133', 20134 : 'Device error 134', 20135 : 'Device error 135', 20136 : 'Device error 136', 20137 : 'Device error 137', 
		20138 : 'Device error 138', 20139 : 'Device error 139', 20140 : 'Device error 140', 20141 : 'Device error 141', 20142 : 'Device error 142', 
		20143 : 'Device error 143', 20144 : 'Device error 144', 20145 : 'df/dt too high', 20146 : 'Device error 146', 20147 : 'Device error 147', 
		20148 : 'Device error 148', 20150 : 'Ierr step too high', 20151 : 'Ierr step too high', 20153 : 'Device error 153', 20154 : 'Shutdown 1', 
		20155 : 'Shutdown 2', 20156 : 'Device error 156', 20157 : 'Insulation fault DC', 20158 : 'Device error 158', 20159 : 'Device error 159', 
		20160 : 'Device error 160', 20161 : 'Device error 161', 20163 : 'Device error 163', 20164 : 'Ierr too high', 20165 : 'No mains', 
		20166 : 'Frequency too high', 20167 : 'Frequency too low', 20168 : 'Mains error', 20169 : 'Vac 10min too high', 20170 : 'Device error 170', 
		20171 : 'Device error 171', 20172 : 'Vac too high', 20173 : 'Vac too low', 20174 : 'Device error 174', 20175 : 'Device error 175', 
		20176 : 'Error DC polarity', 20177 : 'Device error 177', 20178 : 'Device error 178', 20179 : 'Device error 179', 20180 : 'Vdc too low', 
		20181 : 'Blocked external', 20185 : 'Device error 185', 20186 : 'Device error 186', 20187 : 'Device error 187', 20188 : 'Device error 188', 
		20189 : 'L and N interchanged', 20190 : 'Below-average yield', 20191 : 'Limitation error', 20198 : 'Device error 198', 20199 : 'Device error 199', 
		20999 : 'Device error 999'
}


#~~~~~~~~~~~~~~~~~~~   START Functions ~~~~~~~~~~~~~~~~~~~~~~~

# This function will split the csv list into a python list
def retrieve_required_values(required_values_csv):
	required_values = []
	required_values = required_values_csv.split(',')
	return required_values


# This will write a line to the base_directory
def write_line(line, inverter_addr, base_directory, header_line):

	line = line + '\n'

	# Write the log entry, as a date entry in the log directory
	date_str = (time.strftime("%d-%b-%Y"))
	log_filename = date_str + ".csv"
	log_directory = os.path.join(base_directory, inverter_addr)
	write_log(log_directory, log_filename, header_line, line, DEBUG, True, log_directory, "latest.csv")

	return True


# Some of the items need to be converted
def convert_value(key,value):

	# IF its a status code, strip out the first number and find the stua description
	if (key == 'SYS'):
		# Strip out the first CSV
		sys,temp = value.split(',')
		value_int = int(sys, 16)
		# then get the string
		return status_codes[value_int]
	
	# If its a current reading or frequency, divide by 100 to get Amps
	elif ((key == 'IL2') or (key == 'IL1') or (key == 'IL3') or (key == 'IDC') or
         (key == 'TNF')):
		value_int = int(value, 16)
		value_fl = float(value_int)/100.0 
		return (str(value_fl))

	# If its a voltage reading or frequency, divide by 10 to get Volts
	elif ((key == 'UL2') or (key == 'UL1') or (key == 'UL3')):
		value_int = int(value, 16)
		value_fl = float(value_int)/10.0 
		return (str(value_fl))

	# If it's a power of frequency reading, then  divide by 2...for some reason
	elif ((key == 'PAC') or (key == 'PDC')):
		value_int = int(value, 16)
		value_fl = float(value_int) /2.0 
		return (str(value_fl))

	# If the key is empty, return 'no value'
	elif (not value):
		return ''

	else:
		value_str = str(int(value, 16))
		return value_str
	
# This function reads the Solarmax codes frecevied from the inverter
# required_itmes = LIST
# raw_line = STRING
def read_values(required_items, raw_line):
	# For each 'required_item, find it in the raw_line
	# and strip out everything up to a semi-colon or pipe symbol
	errors = False
	data_list = []

	# if the line is empty, return an error
	if (not raw_line):
		return "", True
	
	# Add datetime
	datetime = time.strftime('%Y-%m-%dT%H:%M:%SZ')
	data_list.append(datetime)

	for value in required_items:
		# Find it in the raw line
		found = raw_line.find(value)
		if (found):
			# if found, get everything after the '=' sign
			start = found + len(value) + 1
			# the end is the first '|' or ';' that appears
			found_pipe = 0
			found_semi = 0
			found_pipe = raw_line.find('|',start)
			found_semi = raw_line.find(';',start)
			# Find the lowest number, that is NOT -1 (not found)
			if ((found_pipe != -1) and (found_semi == -1)):
				end = found_pipe
			elif ((found_pipe == -1) and (found_semi != -1)):
				end = found_semi
			elif ((found_pipe < found_semi) and (found_pipe != -1)):
				end = found_pipe
			elif  ((found_semi < found_pipe) and (found_semi != -1)):
				end = found_semi
			else:
				# Flag and error if items not found in both
				errors = True

			# now copy the value
			converted = convert_value(value,raw_line[start:end])
			if (DEBUG > 1):
				print "VALUE: ", value," PIPE: ",found_pipe," SEMI: ",found_semi, "RAW: ", raw_line[start:end], " ITEM: ",converted
			
			data_list.append(converted)
			
		else:
			# flag an error
			errors = True

	# NOTE: Don't need the csv module, since the data is all controlled by this function
	inverter_line = ','.join(data_list)

	if (DEBUG > 1):
		print "Raw line: ",inverter_line, " and errors: ",errors

	return inverter_line, errors


# determines if all the query codes are valid
# returns: True (if all codes are valid), string of comma joined headers
def get_valid_and_header_items(code_list):
	error = False

	header_list = []
	# Check that each type is valid
	for value in required_values:
		if value not in query_dict:
			if (DEBUG > 1):
				print "Value: ",value," not known"
			error = True
		else:
			header_list.append(query_dict[value]);

	# If any errors, then return
	if (error):
		return False,""

	# If no errors, then return a header list
	header_line = ','.join(header_list) + "\n"

	return True, header_line


# Return the HEX Checksum
def hex_checksum(line):
	total = 0
	for char in line:
		total += ord(char)
	# Take the hex value
	check = format(total, '04X')
	return check


# This function will build the Solarmax inverter query string
# required_values = must be a LIST
# inverter_address = MUST be an INT
def construct_inverter_query(inverter_address, required_values):
	error = False

	# convert INT address to HEX, as 2 digit in uppercase
	hex_addr = format(inverter_address, '02X')

	# Check that each type is valid
	for value in required_values:
		if value not in query_dict:
			print "Value: ",value," not known"
			error = True

	# If any errors, then return
	if (error):
		return False

	# Query line will look something like this:
	# {FB;05;4E|64:E1D;E11;E1h;E1m;E1M;E2D;E21;E2h;E2m;E2M;E3D;E31;E3h;E3m;E3M|1270}
	# See this for message format -> https://blog.dest-unreach.be/2009/04/15/solarmax-maxtalk-protocol-reverse-engineered
	
	# Construct the line as follows:
	#
	# 1. Join the required_values into a string separated by semicolons
	joined_values = ';'.join(required_values)
	# 2. Enclose the values in '64:' and the pipe symbols
	query_string = '|64:' + joined_values + '|'
	# 3. Determine the length of the whole string, in HEX
	# 	  So its {AA;BB;CC + query_string + XXXX} ... where AA,BB,CC are always 2 chars, and XXXX is 4 chars
	query_length = 9 + len(query_string) + 5
	query_length_hex = format(query_length, '02X')
	# 4. Add the header to the query
	query_string = 'FB;' + hex_addr + ';' + query_length_hex + query_string
	# 5. Do a checksum on the whole lot and add it to the query string
	check = hex_checksum(query_string)
	query_string = query_string + check
	# 6. Enclose the whole lot in curly braces
	query_string = '{' + query_string + '}'

	return query_string

# Solarmax serial settings
def open_serial_port(serial_dev):
	# open serial port
	serial_port = serial.Serial(port=serial_dev, baudrate=19200, parity=serial.PARITY_NONE, 
										 stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.5 )
	# Flush the inputs and outputs
	serial_port.flushInput()
	serial_port.flushOutput()

	return serial_port

# Close the serial port
def close_serial_port(serial_port):
	# close the serial port
	serial_port.close()

# Send the query to the inverter and read the response
def read_inverter(query_string, serial_port):

	# Flush the inputs and outputs
	serial_port.flushInput()
	serial_port.flushOutput()

	# Encode the command
	if (DEBUG > 1):
		print "Sending the command to the RS485 port: ",query_string 
	serial_port.write(query_string)

	# wait 1 second. Do not make it less than that
	time.sleep(1)

	# read answer line
	response = ''
	while serial_port.inWaiting() > 0:
		response += serial_port.readline()

	if (DEBUG > 1):
			print "Received the following data: ",response

	return response

#~~~~~~~~~~~~~~~~~~~   END Functions ~~~~~~~~~~~~~~~~~~~~~~~

# Check script is run as root
if os.geteuid() != 0:
	print "You need to have root privileges to run this script, or as \'sudo\'. Exiting."
	sys.exit(2)

#check the arguments
arguments = check_args(5)
if (len(arguments) < 5):
	print "The arguments cannot be empty. Usage: ", USAGE
	sys.exit(3)

serial_device = arguments[1]
start_address = arguments[2]
end_address = arguments[3]
log_directory = arguments[4]
required_values_csv = arguments[5]


# If the logging directory doesn't exist, create it
if (not os.path.exists(log_directory)):
	os.makedirs(log_directory)

# Check that no other scripts are running
pidfile = os.path.join(log_directory, PIDFILE)
if check_pidfile(pidfile, DEBUG):
	print "This script is already running"
	sys.exit(1)

# if any args are empty, exit with error
if ((not serial_device) or (not start_address) or (not end_address) or (not log_directory)):
	print "The arguments cannot be empty. Usage: ", USAGE
	sys.exit(4)

# Convert start and stop addresses to INTs
try:
	start_addr = int(start_address)
	end_addr = int(end_address)
except:
	print "Start and stop address must be numbers. Usage: ", USAGE
	sys.exit(5)

# The required values are derived from the list att the top of this script
required_values = retrieve_required_values(required_values_csv)

# Make sure the Solarmax query codes are valid. If not, exit
retval,header_line = get_valid_and_header_items(required_values)
if (not retval):
	print "Some of the Solarmax codes are not valid"
	sys.exit(6)


start_time = time.time()
# Open the serial port
serial_port = open_serial_port(serial_device)

# This will check each inverter. If a bad line is received, it will try one more time
# Sometimes the inverters take 2 goes at getting a good line from the RS485 line
for (inverter_addr) in range(start_addr, end_addr+1):
	count = 2
	# convert an address less than 10 to a leading zero
	# inverter address passed as an INT
	query_string = construct_inverter_query(inverter_addr, required_values)

	while (count >= 1):
		result = read_inverter(query_string, serial_port)
		inverter_line, errors = read_values(required_values, result)
		if (errors == False):
			success = write_line(inverter_line, str(inverter_addr), log_directory, header_line)
			if (success == True):
				break
		count = count - 1


# Close the serial port
close_serial_port(serial_port)

elapsed_time = time.time() - start_time
if (DEBUG > 0):
	print "This request took: ",elapsed_time, " seconds."

# Remove the PID file	
if os.path.isfile(pidfile):
	os.unlink(pidfile)

print 0

