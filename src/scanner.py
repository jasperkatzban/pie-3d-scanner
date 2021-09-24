from serial_cmd import Serial_cmd
from numpy import sin, cos
import csv
  
# Set the name of the serial port.  Determine the name as follows:
#	1) From Arduino's "Tools" menu, select "Port"
#	2) It will show you which Port is used to connect to the Arduino
#
# For Windows computers, the name is formatted like: "COM6"
# For Apple computers, the name is formatted like: "/dev/tty.usbmodemfa141"

ARDUINO_COM_PORT = '/dev/cu.usbmodem1401'
MSG_SCAN_START = 'start'
MSG_SCAN_END = 'done'

file_num_tracker = 0
serial_port = Serial_cmd(ARDUINO_COM_PORT)

# [OLD] open the serial port
# baudRate = 1152000
# serialPort = serial.Serial(ARDUINO_COM_PORT, baudRate, timeout=1)

raw_data = []

def start_reading():
  # raw_data.clear()
  # f = open('data/sensor_reading' + str(file_num_tracker), 'w')
  # writer = csv.writer(f)

def save_data(input_data):
  '''Saves data to a file (or whatever datastructure we use)'''
  split_data = input_data.split(",")
  x = split_data[0]
  y = split_data[1]
  sensor_reading = split_data[2]
  print(sensor_reading)
  raw_data.append([x, y, sensor_reading]) 

def convert_to_cartesian(theta, phi, r):
  '''Converts from spherical coords to cartesian coords'''
  x = r * sin(theta) * cos(phi)
  y = r * sin(theta) * sin(phi)
  z = r * cos(theta)
  return x, y, z

def plot_data(data):
  '''Plots data using matplotlib'''
  pass

def reset():
  if raw_data is not []:
    raw data = []

while serial_port.connected:

  # read msg from serial port
  message = serial_port.read()

  # parse msg type
  if message == MSG_SCAN_START:
    print('Starting scan!')
    reset()
    start_reading()
  elif message == MSG_SCAN_END:
    print('Finished reading data!')
    print(raw_data)
    plot_data()
  else:
    print(f'Saving message: {message}.')
    save_data(message)