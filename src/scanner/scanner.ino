/* 
 * scanner.ino
 * 
 * Created by Kelly Yen, Jasper Katzban & Karen Hinh as 
 * part of the Principles of Integrated Engineering course
 * at Olin College of Engineering.
 * 
 * Facilitates hardware control of pan/tilt servos and measurement 
 * of IR sensor values which are then sent to a Python script via
 * the serial port.
 */

#include <Servo.h>

// set scanning mode for either a 2d array
// of points or 3d point cloud
#define SCAN_MODE_2D true

// define scanning macros
#define RESOLUTION 1 // degree interval per sample
#define NUM_POINTS_THETA 60 // number of samples per axis
#define NUM_POINTS_PHI 60
#define THETA_ANGLE_OFFSET 30 // starting angle offsets
#define PHI_ANGLE_OFFSET 37
#define THETA_CENTER_ANGLE 60
#define PHI_CENTER_ANGLE 65 // origin angle offsets
#define MOVEMENT_DELAY_MS 400 // delay between sampling to allow servos to move
#define NUM_SAMPLES_PER_ANGLE 30 // number of samples to take and average per position

// define start/stop message strings
#define MSG_SCAN_START "start"
#define MSG_SCAN_END "done"

// create servo object to control a servo
Servo servo_theta;
Servo servo_phi;

// define pins
#define SERVO_THETA_PIN 9
#define SERVO_PHI_PIN 10
const uint8_t BUTTON_PIN = 8;
const uint8_t SENSOR_PIN = A0;

// setup serial baud rate
#define SERIAL_BAUD_RATE 115200

// initialize data structure for measured data
int data[NUM_POINTS_THETA][NUM_POINTS_PHI] = {};

// define debounce vars
const uint8_t DEBOUNCE_INTERVAL = 10;
uint32_t debounce_time;
bool button_went_back_low;


// set up serial comms and servos
void setup() {
  Serial.begin(SERIAL_BAUD_RATE); // initialize serial comms
  servo_theta.attach(SERVO_THETA_PIN);  // attaches up/down servo to pin 9
  servo_phi.attach(SERVO_PHI_PIN);      // attaches l/r servo to pin 10
  reset_servos(); // resets to center position
}

// main loop, continually check for input
void loop() {
  uint32_t t; // current time var
  bool button_high; // keep track of switch state
  t = millis(); // set current time timestamp
  // debounce switch input
  if (t >= debounce_time + DEBOUNCE_INTERVAL) {
    button_high = digitalRead(BUTTON_PIN) == HIGH;
    if (button_went_back_low && button_high) {
      // if button is actually pressed, perform scan
      scan();
      button_went_back_low = false;
    } else if (!button_went_back_low && !button_high) {
      button_went_back_low = true;
    }
    debounce_time = t;
  }  
}

// scan across field using servos and sends sensor readings via serial
void scan(){
  Serial.println(MSG_SCAN_START); // send starting message
  if (SCAN_MODE_2D){ // perform scan
    servo_scan_2d(); 
  } else {
    servo_scan_3d(); 
  }
  // print end message and reset servo position
  Serial.println(MSG_SCAN_END);
  reset_servos();
}

// perform 2D scan with one yaw, setting the other to its center angle
void servo_scan_2d(){
  for (int phi = 0; phi <= NUM_POINTS_PHI; phi++) { // iterate over points to sample
    int angle_phi = (phi * RESOLUTION) + PHI_ANGLE_OFFSET; // compute current angle
    servo_phi.write(angle_phi); // write computed angle to servos
    servo_theta.write(THETA_CENTER_ANGLE); 
    float averaged_reading = average_readings(); // average the readings
    delay(MOVEMENT_DELAY_MS); // wait for the servo to reach the position
    send_reading(THETA_CENTER_ANGLE, angle_phi, averaged_reading);
  }
}

// perform scan using both servos
void servo_scan_3d(){
  for (int phi = 0; phi <= NUM_POINTS_PHI; phi++) { // // iterate over points to sample, left and right
    int angle_phi = (phi * RESOLUTION) + PHI_ANGLE_OFFSET; // compute current yaw angle
    for (int theta = 0; theta <= NUM_POINTS_THETA; theta++) { // // iterate over points to sample, up and down
      int angle_theta;
      angle_theta = (theta * RESOLUTION) + THETA_ANGLE_OFFSET; // compute current pitch angle       
      if(phi%2 != 0) { // reverse servo based on yaw parity, zigzagging path
        angle_theta = (NUM_POINTS_THETA*RESOLUTION) - angle_theta + 2*THETA_ANGLE_OFFSET; 
      }
      servo_phi.write(angle_phi); // send angles to servos
      servo_theta.write(angle_theta); 
      delay(MOVEMENT_DELAY_MS); // wait for the servo to reach the position
      float averaged_reading = average_readings(); // take and average readings

      send_reading(angle_theta, angle_phi, averaged_reading); // send reading over serial
    }
  }
}

// send position of servos and sensor reading via serial
void send_reading(int theta, int phi, int sensordata){
  Serial.print(theta);
  Serial.print(",");
  Serial.print(phi);
  Serial.print(",");
  Serial.println(sensordata);
  Serial.flush();
}

// take average of collected readings for a single angle
float average_readings(){
  int s = 0; 
  int numpoints = NUM_SAMPLES_PER_ANGLE;
  for(int i = 0; i < numpoints; i++){
    s += analogRead(SENSOR_PIN); 
    delay(1); // delay and read sensor vals
  }
  return s/numpoints; 
}

// reset servos to center position
void reset_servos() {
  servo_theta.write(THETA_CENTER_ANGLE);
  servo_phi.write(PHI_CENTER_ANGLE);
}