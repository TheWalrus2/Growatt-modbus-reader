#!/usr/bin/env python3.7

import subprocess
from time import strftime
import time
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from urllib.request import urlopen

#settings PVOutput
SYSTEMID ="<YourPVOutputSystemID>"
APIKEY ="<YourPVOutputSystemAPIKEY>"

t_date =format(strftime('%Y%m%d'))
t_time = format(strftime('%H:%M'))

pv_volts1=0.0
pv_volts2=0.0
pv_powerDC1=0.0
pv_powerDC2=0.0
pv_powerAC=0.0
pv_powerPV=0.0
pv1_ACtoday=0.0
pv2_ACtoday=0.0
Wh_total=0
current_temp=0.0
EACToday=0.0
voltage1=0.0
voltage2=0.0
voltage3=0.0

for i in range(1):
# Read data from inverter
  inverter = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, stopbits=1, parity='N', bytesize=8, timeout=1)
  inverter.connect()
  rr = inverter.read_input_registers(1,99)
  inverter.close()

  value=rr.registers[53]
  EACToday=EACToday+(float(value)/10)

  value=rr.registers[1]
  pv_powerPV=pv_powerPV+(float(value)/10)
  if pv_powerPV < 0:
    pv_powerPV = 0

  value=rr.registers[2]
  pv_volts1=pv_volts1+(float(value)/10)
  if pv_volts1 < 0:
    pv_volts1 = 0

  value=rr.registers[6]
  pv_volts2=pv_volts2+(float(value)/10)
  if pv_volts2 < 0:
    pv_volts2 = 0

  value=rr.registers[5]
  pv_powerDC1=pv_powerDC1+(float(value)/10)
  if pv_powerDC1 < 0:
    pv_powerDC1 = 0
  
  value=rr.registers[9]
  pv_powerDC2=pv_powerDC2+(float(value)/10)
  if pv_powerDC2 < 0:
    pv_powerDC2 = 0
  
  value=rr.registers[35]
  pv_powerAC=pv_powerAC+(float(value)/10)
  if pv_powerAC < 0 or pv_powerAC > 6200:
    pv_powerAC = 0
 
  value=rr.registers[55]
  Wh_total=Wh_total+(float(value)/10)
  
  value=rr.registers[59]
  pv1_ACtoday=pv1_ACtoday+(float(value)/10)
  if pv1_ACtoday < 0:
    pv1_ACtoday = 0
  
  value=rr.registers[63]
  pv2_ACtoday=pv2_ACtoday+(float(value)/10)
  if pv2_ACtoday < 0:
    pv2_ACtoday = 0

  value=rr.registers[93]
  current_temp=current_temp+(float(value)/10)

  value=rr.registers[37]
  voltage1=voltage1+(float(value)/10)  
  if voltage1 < 0:
    voltage1 = 0

  value=rr.registers[41]
  voltage2=voltage2+(float(value)/10)  
  if voltage2 < 0:
    voltage2 = 0

  value=rr.registers[45]
  voltage3=voltage3+(float(value)/10)  
  if voltage3 < 0:
    voltage3 = 0

# sent all to PVOutput
if pv_powerAC > 0:
  cmd=('curl -d "d=%s" -d "t=%s" -d "v2=%s" -d "c1=0" -H \
  "X-Pvoutput-Apikey: %s" -H \
  "X-Pvoutput-SystemId: %s" \
  http://pvoutput.org/service/r2/addstatus.jsp'\
  %(t_date, t_time, pv_powerAC, \
  APIKEY, SYSTEMID))
  ret = subprocess.call(cmd, shell=True)

# sent all to Domoticz
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=20&nvalue=0&svalue=' + str(pv_powerDC1))
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=21&nvalue=0&svalue=' + str(pv_powerDC2))
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=26&nvalue=0&svalue=' + str(pv_powerAC) + ';' + str(EACToday*1000))
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=27&nvalue=0&svalue=' + str(Wh_total))
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=49&nvalue=0&svalue=' + str(pv_powerDC1)+str(';')+str(pv1_ACtoday))
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=50&nvalue=0&svalue=' + str(pv_powerDC2)+str(';')+str(pv2_ACtoday))
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=51&nvalue=0&svalue=' + str(pv_powerPV))
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=69&nvalue=0&svalue=' + str(voltage1))
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=70&nvalue=0&svalue=' + str(voltage2))
urlopen ('http://<YourDomticxServerIP>:<DomoticzPort>/json.htm?type=command&param=udevice&idx=71&nvalue=0&svalue=' + str(voltage3))



# print all for Debug
print (' ')
print ('EACToday %s' %EACToday)
print ('pv_powerPV %s' %pv_powerPV)
print ('pv_volts1 %s' %pv_volts1)
print ('pv_volts2 %s' %pv_volts2)
print ('pv_powerDC1 %s' %pv_powerDC1)
print ('pv_powerDC2 %s' %pv_powerDC2)
print ('pv1_ACtoday %s' %pv1_ACtoday)
print ('pv2_ACtoday %s' %pv2_ACtoday)
print ('pv_powerAC %s' %pv_powerAC)
print ('Wh_total %s' %Wh_total)
#print ('current_temp %s' %current_temp)1twea