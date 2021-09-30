#include <Servo.h>

// define measurement resolution
#define RESOLUTION 0.5
#define NUM_POINTS_THETA 80 
#define NUM_POINTS_PHI 80
#define THETA_ANGLE_OFFSET 35
#define PHI_ANGLE_OFFSET 45
#define THETA_CENTER_ANGLE 90
#define PHI_CENTER_ANGLE 90
#define MOVEMENT_DELAY_MS 100

// create servo object to control a servo
Servo servo_theta;
Servo servo_phi;

// define pins
#define SERVO_THETA_PIN 9
#define SERVO_PHI_PIN 10
#define SERIAL_BAUD_RATE 115200
const uint8_t BUTTON_PIN = 8;
const uint8_t SENSOR_PIN = A0;

// initialize data structure for measured data
int data[NUM_POINTS_THETA][NUM_POINTS_PHI] = {}; 

// define debounce vars
const uint8_t DEBOUNCE_INTERVAL = 10;
uint32_t debounce_time;
bool button_went_back_low;

bool oneservo = false; 

// set up serial comms and servos
void setup() {
  Serial.begin(SERIAL_BAUD_RATE); // initialize serial comms
  servo_theta.attach(SERVO_THETA_PIN);  // attaches up/down servo to pin 9
  servo_phi.attach(SERVO_PHI_PIN);      // attaches l/r servo to pin 10
  reset_servos();
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
  Serial.println("start");
  if (oneservo){
    one_servo_scan(); 
  } else {
    two_servo_scan(); 
  }
  
  Serial.println("done");
  reset_servos();
}

void one_servo_scan(){
  for (int phi = 0; phi <= NUM_POINTS_PHI; phi++) { // left and right
    int angle_phi = (phi * RESOLUTION) + PHI_ANGLE_OFFSET;
    servo_phi.write(angle_phi);
    servo_theta.write(THETA_CENTER_ANGLE); 
    float averaged_reading = average_readings();
    delay(MOVEMENT_DELAY_MS); // wait for the servo to reach the position
    send_reading(THETA_CENTER_ANGLE, angle_phi, averaged_reading);
  }
}

void two_servo_scan(){
  for (int phi = 0; phi <= NUM_POINTS_PHI; phi++) { // left and right
    int angle_phi = (phi * RESOLUTION) + PHI_ANGLE_OFFSET;
    for (int theta = 0; theta <= NUM_POINTS_THETA; theta++) { // up and down
      int angle_theta;
      angle_theta = (theta * RESOLUTION) + THETA_ANGLE_OFFSET;         
      if(phi%2 != 0) {
        angle_theta = (NUM_POINTS_THETA*RESOLUTION) - angle_theta + 2*THETA_ANGLE_OFFSET; 
      }
      servo_phi.write(angle_phi);
      servo_theta.write(angle_theta); 
      float averaged_reading = average_readings();
      delay(MOVEMENT_DELAY_MS); // wait for the servo to reach the position

      send_reading(angle_theta, angle_phi, averaged_reading);
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

float average_readings(){
  int s = 0; 
  int numpoints = 10; 
  for(int i = 0; i < numpoints; i++){
    delay(1);
    s += analogRead(SENSOR_PIN); 
  }
  return s/numpoints; 
}
  

// reset servos to center position
void reset_servos() {
  servo_theta.write(THETA_CENTER_ANGLE);
  servo_phi.write(PHI_CENTER_ANGLE);
}