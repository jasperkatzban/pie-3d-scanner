from serial_cmd import Serial_cmd
from numpy import sin, cos, mgrid, power, empty, array2string, zeros, sqrt
from numpy.random.mtrand import randint
from matplotlib import cbook
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import csv
from sys import exit

LOCAL_TEST = True

MSG_SCAN_START = 'start'
MSG_SCAN_END = 'done'
RESOLUTION = 1
NUM_POINTS_THETA = 50
NUM_POINTS_PHI = 50
THETA_ANGLE_OFFSET = 25
PHI_ANGLE_OFFSET = 55

file_num_tracker = 0

#TODO: turn this into a class structure
#TODO: optionally accept scan resolution as arg
serial_port = Serial_cmd()
print('Ready to scan! Press the button on the breadboard to begin.')

spherical_data = empty(shape=(NUM_POINTS_THETA,NUM_POINTS_PHI), dtype=float)
cartesian_data_x = empty(shape=(NUM_POINTS_THETA,NUM_POINTS_PHI), dtype=float)
cartesian_data_y = empty(shape=(NUM_POINTS_THETA,NUM_POINTS_PHI), dtype=float)
cartesian_data_z = empty(shape=(NUM_POINTS_THETA,NUM_POINTS_PHI), dtype=float)

def save_to_file(data):
  global file_num_tracker
  with open('data/sensor_reading_' + str(file_num_tracker), 'w') as csv:
    csv.write(array2string(data))
    
  file_num_tracker += 1

def save_data(input_data):
  '''Saves raw input to a list in the format [[theta, phi, radius]...]'''
  theta, phi, sensor_reading = parse_message(message)
  r = calibrate(sensor_reading)
  
  index_x, index_y = int((theta-THETA_ANGLE_OFFSET)/RESOLUTION), int((phi-PHI_ANGLE_OFFSET)/RESOLUTION)
  spherical_data[index_x, index_y] = r
  x, y, z = convert_to_cartesian(theta, phi, r)
  cartesian_data_x[index_x, index_y] = x
  cartesian_data_y[index_x, index_y] = y
  cartesian_data_z[index_x, index_y] = z
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
def plot_data(data, title=''):
  '''Plots data using matplotlib'''
  ls = LightSource(azdeg=315, altdeg=45)
  plt.imshow(ls.hillshade(data), cmap='gray')
  plt.title(title)
  plt.xlabel('Yaw (Degrees)')
  plt.ylabel('Pitch (Degrees)')
  plt.colorbar()
  plt.show()

def reset():
  '''Resets program'''
  pass

def generate_test_data_rand():
  '''Generates randomized test data'''
  r = randint(0, 1024, size=(NUM_POINTS_THETA, NUM_POINTS_PHI))
  return r

def generate_test_data_func():
  '''Generates test data based on a circular sin func'''
  x_bound, y_bound = int(NUM_POINTS_THETA/2), int(NUM_POINTS_PHI/2)
  x, y = mgrid[-x_bound:x_bound:.1, -y_bound:y_bound:.1]
  r = 5 * (sqrt(x**2 + y**2) + sin(x**2 + y**2))
  return r

if LOCAL_TEST:
  plot_data(generate_test_data_func(), 'Test Data')
else:
  while serial_port.connected:
    # read msg from serial port
    message = serial_port.read()
    print(f'Received message: {message}')
    # parse msg type
    if MSG_SCAN_START in message:
      print('Starting scan!')
      reset()
    # when done, plot data and exit
    elif MSG_SCAN_END in message:
      print('Finished reading data!')
      print('Spherical Data:\n')
      print(spherical_data)
      # print('Cartesian Data:\n')
      # print(cartesian_data_x)
      save_to_file(spherical_data)
      save_to_file(cartesian_data_x)
      save_to_file(cartesian_data_y)
      save_to_file(cartesian_data_z)
      plot_data(cartesian_data_x, 'Cartesian Data (X), Calibrated')
      plot_data(cartesian_data_y, 'Cartesian Data (Y), Calibrated')
      plot_data(cartesian_data_z, 'Cartesian Data (Z), Calibrated')
      exit(0)
    # otherwise, assume message is data and parse
    else:
      print(f'Saving data')
      save_data(message)