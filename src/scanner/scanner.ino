/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 https://www.arduino.cc/en/Tutorial/LibraryExamples/Sweep
*/

#include <Servo.h>

// define measurement resolution
#define RESOLUTION 5
#define NUM_POINTS_THETA 18
#define NUM_POINTS_PHI 18
#define THETA_ANGLE_OFFSET 45
#define PHI_ANGLE_OFFSET 45

// create servo object to control a servo
Servo servo_theta;
Servo servo_phi;

// define pins
const int BUTTON_PIN = 8;
const int SENSOR_PIN = A0;

// initialize data structure for measured data
int data[NUM_POINTS_THETA][NUM_POINTS_PHI] = {}; 

// define debounce vars
const uint8_t DEBOUNCE_INTERVAL = 10;
uint32_t debounce_time;
bool button_went_back_low;

void setup() {
  long baudRate = 115200; // initialize serial comms
  Serial.begin(115200);
  servo_theta.attach(9);  // attaches the servo on pin 9 to the servo object
  servo_phi.attach(10);
}

void loop() {
  uint32_t t; // current time var
  bool button_high; // keep track of switch state
  
  t = millis(); // set current time timestamp
  
  // when button is clicked, switch mode
  // debounce switch input
  if (t >= debounce_time + DEBOUNCE_INTERVAL) {
    button_high = digitalRead(BUTTON_PIN) == HIGH;
    if (button_went_back_low && button_high) {
      // if button is actually pressed
      scan(); // scan the field
      // send_captured_data(); // send data via serial port
      button_went_back_low = false;
    } else if (!button_went_back_low && !button_high) {
      button_went_back_low = true;
    }
    debounce_time = t;
  }  
}

// scan across field using servos
void scan(){
  for (int theta = 0; theta < NUM_POINTS_THETA; theta++) { // goes from 0 degrees to 180 degrees
    int angle_theta = (theta * RESOLUTION) + THETA_ANGLE_OFFSET;
    servo_theta.write(angle_theta); 
    for (int phi = 0; phi < NUM_POINTS_PHI; phi++) { // goes from 180 degrees to 0 degrees  
      int angle_phi;
      if(theta%2 == 0){
        angle_phi = phi * RESOLUTION + PHI_ANGLE_OFFSET;         
      } else {
        angle_phi = 180 - phi * RESOLUTION + PHI_ANGLE_OFFSET; 
      }
      servo_phi.write(angle_phi);
      delay(100);                       // waits 100 ms for the servo to reach the position
      int sensor_val = analogRead(SENSOR_PIN); 
      send_position(theta, phi, sensor_val);
    }
  }
  Serial.print("done"); 
}

void save_position(int theta, int phi, int sensordata){
  data[theta][phi] = sensordata; 
}

void send_position(int theta, int phi, int sensordata){
  Serial.print(theta * RESOLUTION);
  Serial.print(",");
  Serial.print(phi * RESOLUTION);
  Serial.print(",");
  Serial.println(sensordata);
  Serial.flush();
}