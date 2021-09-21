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
#define NUM_POINTS_Y 36
#define NUM_POINTS_X 36

// create servo object to control a servo
Servo servo_y;
Servo servo_x;

// define pins
const int BUTTON_PIN = 8; 
const int SENSOR_PIN = A0; 

// initialize data structure for measured data
int data[NUM_POINTS_Y][NUM_POINTS_X] = {}; 

// define debounce vars
const uint8_t DEBOUNCE_INTERVAL = 10;
uint32_t debounce_time;
bool button_went_back_low;

void setup() {
  long baudRate = 115200; // initialize serial comms
  Serial.begin(115200);
  servo_y.attach(9);  // attaches the servo on pin 9 to the servo object
  servo_x.attach(10);
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
  for (int y = 0; y < 36; y++) { // goes from 0 degrees to 180 degrees
    int angle_y = y * RESOLUTION;
    servo_y.write(angle_y); 
    for (int x = 0; x < 36; x++) { // goes from 180 degrees to 0 degrees  
      int angle_x;
      if(y%2 == 0){
        angle_x = x * RESOLUTION;         
      } else {
        angle_x = 180 - x * RESOLUTION; 
      }
      servo_x.write(angle_x);
      delay(100);                       // waits 100 ms for the servo to reach the position
      int sensor_val = analogRead(SENSOR_PIN); 
      send_position(y, x , sensor_val); 
    }
  }
}

void save_position(int y, int x, int sensordata){
  data[y][x] = sensordata; 
}

void send_position(int y, int x, int sensordata){
  Serial.print(y * RESOLUTION);
  Serial.print(",");
  Serial.print(x * RESOLUTION);
  Serial.print(",");
  Serial.println(sensordata);
  Serial.flush();
}