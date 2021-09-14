/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 https://www.arduino.cc/en/Tutorial/LibraryExamples/Sweep
*/

#include <Servo.h>

Servo myservo1;  // create servo object to control a servo
Servo myservo2;
// twelve servo objects can be created on most boards


const int BUTTON_PIN = 8; 

int servo1_pos = 0;    // variable to store the servo position
int servo2_pos = 0; 

int currentState; 

// define debounce vars
const uint8_t DEBOUNCE_INTERVAL = 10;
uint32_t debounce_time;
bool button_went_back_low;
uint16_t buttonmode = 0;

void setup() {
  myservo1.attach(9);  // attaches the servo on pin 9 to the servo object
  myservo2.attach(10);
}

void loop() {
  uint32_t t; // current time var
  bool button_high; // keep track of switch state
  
  t = millis(); // set current time timestamp
  
  //when button is clicked, switch mode
  // debounce switch input
  if (t >= debounce_time + DEBOUNCE_INTERVAL) {
    button_high = digitalRead(BUTTON_PIN) == HIGH;
    if (button_went_back_low && button_high) {
      // if button is actually pressed
      scan(); 
      buttonmode = buttonmode%5 + 1;
      Serial.println(buttonmode);
      button_went_back_low = false;
    } else if (!button_went_back_low && !button_high) {
      button_went_back_low = true;
    }
    debounce_time = t;
  }  
}

void scan(){
  for (int pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo1.write(pos);
    myservo2.write(pos);               // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15 ms for the servo to reach the position
  }
  for (int pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo1.write(pos);   
    myservo2.write(pos);            // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15 ms for the servo to reach the position
  }

}