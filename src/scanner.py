 # scanner.py
 # 
 # Created by Kelly Yen, Jasper Katzban & Karen Hinh as 
 # part of the Principles of Integrated Engineering course
 # at Olin College of Engineering.
 # 
 # Facilitates recording, and processing, and visualization
 # of measurements obtained from the Arduino.

from serial_cmd import Serial_cmd
from numpy import sin, cos, exp
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from math import radians
import csv
from sys import exit

SCAN_MODE = '3D' # macro to specify scanning mode. Set to '2D' or '3D'

# scanning macros, must correspond macros in scanner.ino
MSG_SCAN_START = 'start' # start and stop message strings
MSG_SCAN_END = 'done'
RESOLUTION =  1 # degree interval per sample
NUM_POINTS_THETA = 60 # number of samples per axis
NUM_POINTS_PHI = 60
THETA_ANGLE_OFFSET = 30 # starting angle offsets
PHI_ANGLE_OFFSET = 45
THETA_CENTER_ANGLE = 60 # origin angle offsets
PHI_CENTER_ANGLE = 65

MIN_CM_DISTANCE_Y = 40 # distance thresholds to filter out foreground / background
MAX_CM_DISTANCE_Y = 48

file_num_tracker = 0 # increment file saving number

cartx   = [] # initialize global coord lists
carty   = []
cartz   = []
allcart = []
rawdata = [] 

def record_data(message):
  '''Saves a single raw input message consisting of angles and sensor reading
     to a list in the format [[theta, phi, radius],...]'''
  theta, phi, sensor_reading = parse_message(message) # parse msg into individual values
  r = calibrate(sensor_reading) # apply calibration curve to incoming data
  rawdata.append([theta, phi, sensor_reading]) # add to data pool
  x, y, z = convert_to_cartesian(theta, phi, r) # change to cartesian coord system
  cartx.append(x) # add values to coord lists
  carty.append(y)
  cartz.append(z)
  allcart.append([x, y, z])
  print(f'Params - theta: {theta}\tphi: {phi}\tSensor: {sensor_reading}\tr: {r:.2f}\t x: {x:.2f}\t y:{y:.2f}\tz: {z:.2f}')

def save_to_file(data):
  '''Saves a CSV file containing scanned data to a file'''
  global file_num_tracker
  with open('data/sensor_reading_' + str(file_num_tracker) + '.csv', 'w') as csv:
    csv.write(str(data))
    
  file_num_tracker += 1

def parse_message(message):
  '''Splits incoming message from Arduino into individual values,
     delimited by commas'''
  split_data = message.split(",")
  return [int(value) for value in split_data]

def calibrate(sensor_reading):
  '''Convert from a sensor reading to distance'''
  voltage = sensor_reading * 5 /1024 # use fitted calibration curve
  return 155 * exp(-0.987* voltage) # convert to distance measurement

def convert_to_cartesian(theta, phi, r):  
  '''Converts from spherical coords to cartesian coords'''
  x = r * sin(radians(phi)) * cos(radians(theta))
  y = r * cos(radians(theta)) * cos(radians(phi))
  z = r * sin(radians(theta))
  return x, y, z

def read_and_plot(fname):
  '''Reads processed data from a csv file who's path is passed in as an arg,
     plots in either 2D or 3D according to SCAN_MODE macro'''
  l = [] # create empty filtered coord lists
  x = []
  y = []
  z = [] 
  with open(fname, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
      l = list(line)

  # remove brackets from data and parse to float
  tracker = 0
  for i, item in enumerate(l):
    replaced = float(item.replace("[", "").replace("]","")) 
    if tracker == 0:
      x.append(replaced)
    elif tracker == 1:
      y.append(replaced)
    else: 
      z.append(replaced)
    tracker += 1
    if tracker > 2:
      tracker = 0 
  
  if SCAN_MODE == '2D': # plot data 
    create_2d_plot(x, y)
  elif SCAN_MODE == '3D':
    create_3d_plot(x, y, z)

def read_and_plot_raw(fname):
  '''Reads raw data from a csv file who's path is passed in as an arg,
     plots in either 2D or 3D according to SCAN_MODE macro'''

  l     = [] # create empty filtered coord lists
  theta = []
  phi   = []
  r     = []

  with open(fname, 'r') as csvfile: # open and parse readings in file
    reader = csv.reader(csvfile)
    for line in reader:
      l = list(line)

  # remove brackets from data and parse to floats
  tracker = 0
  for i, item in enumerate(l):
    replaced = float(item.replace("[", "").replace("]",""))
    if tracker == 0:
      theta.append(replaced)
    elif tracker == 1:
      phi.append(replaced)
    else: 
      r.append(calibrate(replaced))
    tracker += 1
    if tracker > 2:
      tracker = 0 

  x_filtered = [] # create empty filtered coord lists
  y_filtered = []
  z_filtered = [] 

  # iterate over readings and add to filtered list for plotting
  for i in range(len(theta)):
    theta[i] -= THETA_ANGLE_OFFSET + 20 # correct for angle offset
    phi[i] -= PHI_CENTER_ANGLE
    x, y, z = convert_to_cartesian(theta[i], phi[i], r[i])
    if y >= MIN_CM_DISTANCE_Y and y <= MAX_CM_DISTANCE_Y: # threshold values based on y position
      x_filtered.append(x)
      y_filtered.append(y)
      z_filtered.append(z)

  if SCAN_MODE == '2D': # plot data 
    create_2d_plot(x_filtered, y_filtered)
  elif SCAN_MODE == '3D':
    create_3d_plot(x_filtered, y_filtered, z_filtered)

def create_2d_plot(x, y):
  '''Creates a 2D scatter plot of measured point cloud data in a single plane'''
  plt.scatter(x, y)
  plt.title('2D IR Sensor Data, Unfiltered')
  plt.xlabel('X Position (cm)')
  plt.ylabel('Y Position (cm)')
  plt.xlim(-40,40)
  plt.ylim(0,100)

  plt.show()

def create_3d_plot(x, y, z):
  '''Creates a 3D scatter plot of measured point cloud data'''
  fig = plt.figure()
  ax = plt.axes(projection='3d')
  ax.scatter3D(x, y, z, s = 1)
  ax.set_title('3D IR Sensor Data, Unfiltered')
  ax.set_ylabel('Y Position (cm)')
  ax.set_xlabel('X Position (cm)')
  ax.set_zlabel('Z Position (cm)')
  ax.set_xlim(-40,40)
  ax.set_ylim(0,100)
  ax.set_zlim(-15,50)

  plt.show()

serial_port = Serial_cmd() # attempt to open serial port and run scan

if serial_port.connected:
  print('Ready to scan! Press the button on the breadboard to begin.')

  # main loop, takes start/stop commands and measurements from
  # serial port and delegates storage, processing, and plotting.
  while serial_port.connected:
    message = serial_port.read() # read msg from serial port
    print(f'Received message: {message}')
    
    if MSG_SCAN_START in message: # parse msg type
      print('Starting scan!')
    
    elif MSG_SCAN_END in message: # when done, plot raw data and exit
      print('Finished reading data! Saving to file.')
      save_to_file(rawdata) # save raw data to file

      if SCAN_MODE == '2D': # plot depending on scanning mode
        create_2d_plot(cartx, carty)
      elif SCAN_MODE == '3D':
        create_3d_plot(cartx, carty, cartz)
      exit(0)
    
    else: # otherwise, assume message is data and parse
      print(f'Saving data')
      record_data(message)
      
else:
  # if running without serial port, open specified csv files and
  # perform filtering/plotting
  print('Processing and plotting data from saved files.')
  try:
    if SCAN_MODE == '2D':
      read_and_plot_raw('./data/sensor_reading_2D.csv')
    elif SCAN_MODE == '3D':
      read_and_plot_raw('./data/sensor_reading_3D.csv')
  except FileNotFoundError:
    print('Error: No file found at specified path! Please try again.')