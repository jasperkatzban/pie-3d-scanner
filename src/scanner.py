from serial_cmd import Serial_cmd
from numpy import sin, cos, mgrid, power, empty
from numpy.random.mtrand import randint
from matplotlib import cbook
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import csv
from sys import exit

MSG_SCAN_START = 'start'
MSG_SCAN_END = 'done'
RESOLUTION = 5
NUM_POINTS_THETA = 18
NUM_POINTS_PHI = 18
THETA_ANGLE_OFFSET = 45
PHI_ANGLE_OFFSET = 45

file_num_tracker = 0

#TODO: turn this into a class structure
#TODO: optionally accept scan resolution as arg
serial_port = Serial_cmd()
print('Ready to scan! Press the button on the breadboard to begin.')

spherical_data = empty(shape=(NUM_POINTS_THETA,NUM_POINTS_PHI), dtype=float)
cartesian_data = empty(shape=(NUM_POINTS_THETA,NUM_POINTS_PHI), dtype=float)

# TODO: optionally write to file
def start_reading():
  '''Writes recorded data to a file'''
  # spherical_data.clear()
  # f = open('data/sensor_reading' + str(file_num_tracker), 'w')
  # writer = csv.writer(f)
  pass

def save_data(input_data):
  '''Saves raw input to a list in the format [[theta, phi, radius]...]'''
  theta, phi, sensor_reading = parse_message(message)
  r = calibrate(sensor_reading)
  
  index_x, index_y = int((theta-THETA_ANGLE_OFFSET)/RESOLUTION)-1, int((phi-PHI_ANGLE_OFFSET)/RESOLUTION)-1
  spherical_data[index_x, index_y] = r
  x, y, z = convert_to_cartesian(theta, phi, r)
  cartesian_data[index_x, index_y] = z
  print(f'Params - theta: {theta}\tphi: {phi}\tSensor: {sensor_reading}\tr: {r:.2f}\t x: {x:.2f}\t y:{y:.2f}\tz: {z:.2f}')

def convert_to_cartesian(theta, phi, r):
  '''Converts from spherical coords to cartesian coords'''
  x = r * sin(theta) * cos(phi)
  y = r * sin(theta) * sin(phi)
  z = r * cos(theta)
  return x, y, z

def calibrate(sensor_reading):
  '''Convert from a sensor reading to distance'''
  return 122475 * (sensor_reading)**-1.57

def parse_message(message):
  split_data = message.split(",")
  return [int(value) for value in split_data]

#TODO: plot with units, maybe plot cartesian data too
def plot_data(data):
  '''Plots data using matplotlib'''
  ls = LightSource(azdeg=315, altdeg=45)
  plt.imshow(ls.hillshade(data), cmap='gray')
  plt.title('Spherical Data, Calibrated')
  plt.xlabel('Yaw (Degrees)')
  plt.ylabel('Pitch (Degrees)')
  plt.colorbar()
  plt.show()

def reset():
  '''Resets program'''
  pass

def generate_test_data():
  '''Generates randomized test data'''
  r = randint(0, 1024, size=(NUM_POINTS_THETA, NUM_POINTS_PHI))
  return r

while serial_port.connected:
  # read msg from serial port
  message = serial_port.read()
  print(f'Received message: {message}')
  # parse msg type
  if MSG_SCAN_START in message:
    print('Starting scan!')
    reset()
    start_reading()
  # when done, plot data and exit
  elif MSG_SCAN_END in message:
    print('Finished reading data!')
    plot_data(spherical_data)
    exit(0)
  # otherwise, assume message is data and parse
  else:
    print(f'Saving data')
    save_data(message)