
# Purpose
The purpose of this project is to collect from Solarmax Inverters and send the data to your cloud using Ardexa. Data from Solarmax solar inverters is read using an RS485 connection and a Linux device such as a Raspberry Pi, or an X86 intel powered computer. 

## How does it work
This application is written in Python, to query Solarmax inverters connected via RS485. This application will query 1 or more connected inverters at regular intervals. Data will be written to log files on disk in a directory specified in the script. Usage and command line parameters are as follows:

This script will query a Solarmax inverter. Usage: python solarmax-ardexa.py {serial device} {Start Address} {End Address} {log directory} {Comma separated list of values}, where...
{serial device} = ..something lie: /dev/ttyS0
{Start Address} = start range 1-32 of the RS485 address
{End Address} = end range 1-32 of the RS485 address
{log directory} = logging directory
{Comma separated list of values} = list of "query_dict" values below as a single string with no spaces, like: KDY,IL1,IL2,IL3,PAC,PDC,TNF,TKK,SYS,KHR,KMT,KLM,UL1,UL2,UL3,PRL
eg: python solarmax-ardexa.py /dev/ttyS0 1 5 /opt/ardexa/solarmax/logs KDY,IL1,IL2,IL3,PAC,PDC,TNF,TKK,SYS,KHR,KMT,KLM,UL1,UL2,UL3,PRL

The debug level can be changed at line 38 or so of the python script (`solarmax-ardexa.py`)
```
DEBUG = 0
```

## RS485 to USB converter
Solarmax inverters can use RS485 as a means to communicate data and settings
RS485 is a signalling protocol that allows many devices to share the same physical pair of wires, in a master master/slave relationship
See -> http://www.usb-serial-adapter.org/ for further information

When an RS485 to USB converter has been plugged in, on Linux systems the device will connect to something line /dev/ttyUSB0. To check:
```
sudo tail -f /var/log/syslog
...then plug in the converter
```
You should see a line like: `usb 1-1.4: ch341-uart converter now attached to ttyUSB0`
This means that the RS485 serial port can be accessed by the logical device `/dev/ttyUSB0`
Alternatively, try: `dmesg | grep tty`

## Inverter to RS485 (DB9) Physical Connection
If your computer has an RS485 port, then the inverter can be connected directly to this port.
The inverter is connected using 3 wires to the RS485 DB9 port on the computer. DO NOT connect the inverter RS485 to a RS232 port. They are not voltage compatible and damage will probably occur. For this to happen, you need a devices like these:
- http://www.robotshop.com/en/db9-female-breakout-board.html
- https://core-electronics.com.au/db9-female-breakout-board.html
- https://www.amazon.com/Female-Breakout-Board-Screw-Terminals/dp/B00CMC1XFU

Each and every RS485 port that uses DB9 has a different pinout. So you have to read the actual manual for the physical RS485 port you are using. 
For example; if using the Advantech UNO 2362G, the following pins are used: Pin1 = D- , Pin 2 = D+ and Pin 5 = GND. All other pins are not connected, so do not connect any other pins. 
So to wire it all up:
- Make sure the Advantech is turned off
- D+ Pin from the Solarmax Inverter (should be Pin 2 on the RS485 inverter interface) to Pin 2 of the RS485 DB-9 (Female) on the Advantech UNO 2362G
- GND Pin from the Solarmax Inverter (should be Pin 5 on the RS485 inverter interface) to Pin 5 of the RS485 DB-9 (Female) on the Advantech UNO 2362G
- D- Pin from the Solarmax Inverter (should be Pin 7 on the RS485 inverter interface) to Pin 1 of the RS485 DB-9 (Female) on the Advantech UNO 2362G

Confirm the physical serial port by running the command `dmesg | grep tty`. As stated previously, it should return something like `/dev/ttyS1` if using a serial com port, or something like `/dev/ttyUSB0` if using a 485/USB serial converter.

## The Solarmax Protocol
Solarmax (http://http://www.solarmax.com/) supply supply retail and commercial grade Solar PV inverters. This python script is designed to collect data from Solarmax inverters, using RS485 connected devices. Contact us to help you with adapting this script to collect from other Solarmax inverters.

## How to use the script
On a raspberry Pi, or other Linux machines (arm, intel, mips or whetever), make sure Python is installed (which it should be). Then install the `pyserial` dependancies as follows:
```
sudo apt-get update
sudo apt-get install python-pip
sudo pip install pyserial
```

Then install and run it as follows:
Note that the applications should be run as root only since needs access to a device in the `/dev` directory. 
```
cd
git https://github.com/ardexa/solarmax-inverters.git
cd solarmax-inverters
python solarmax-ardexa.py {serial device} {Start Address} {End Address} {log directory} {Comma separated list of values}
...eg: python solarmax-ardexa.py /dev/ttyS0 1 5 /opt/ardexa/solarmax/logs KDY,IL1,IL2,IL3,PAC,PDC,TNF,TKK,SYS,KHR,KMT,KLM,UL1,UL2,UL3,PRL

```


## Collecting to the Ardexa cloud
Collecting to the Ardexa cloud is free for up to 3 Raspberry Pis (or equivalent). Ardexa provides free agents for ARM, Intel x86 and MIPS based processors. To collect the data to the Ardexa cloud do the following:
a. Create a `RUN` scenario to schedule the Ardexa Solarmax script to run at regular intervals (say every 300 seconds/5 minutes).
b. Then use a `CAPTURE` scenario to collect the csv (comma separated) data from the filename `/opt/ardexa/Solarmax/logs/`. This file contains a header entry (as the first line) that describes the CSV elements of the file.

## Help
Contact Ardexa at support@ardexa.com, and we'll do our best efforts to help.


