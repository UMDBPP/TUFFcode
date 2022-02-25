/*===========================================================================
 * T.U.F.F (Tension Under Flight Forces) UMD BPP 
 * Hertz rate checker
 * By Jeremy Kuznetsov and Jaxon Lee
 * 
 * This gives the hertz rate of a particular block of code. 
 * Useful for debugging bottlenecks in sampling rate.
 * 
 ===========================================================================*/

// Librariess
#include <HX711.h>              // HX711 0.7.5 by Bogdan Necula
#include <SPI.h>                // Built in
#include <SD.h>                 // Built in
#include <Wire.h>               // Built in
#include <RTClib.h>             // RTClib 2.0.2 by Adafruit. NOTE: Dependent on BusIO 1.11.1 by Adafruit.
#include <Adafruit_BMP280.h>    // BMP280 2.6.1 by Adafruit. NOTE: Dependent on Adafruit Unified Sensor 1.1.4 by Adafruit


// Declaring Objects
HX711 loadcell;
RTC_DS1307 rtc;


// Wiring for the HX711 Amplifier
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

int counter = 0;
DateTime timeLog;

/*===========================================================================
 * Setup
 * Initialize the loadcell and prepare it for accurate readings.
 =========================================================================== */

void setup() {
  Serial.begin(9600);
  Serial.println("BEGIN HERTZ CHECKER CODE");

  // Declare LED as an output pin and turn it off
  pinMode(LED_BUILTIN, OUTPUT); 
  digitalWrite(LED_BUILTIN, LOW);

  // Initialize HX711 with pinning.
  loadcell.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);  

  // Reset or "zero" loadcell readings.
  loadcell.set_scale();
  loadcell.tare();

  // Wait for RTC to respond
  if(!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    while (1) delay(10);
  }

  rtc.begin();

  // Set RTC Date/Time
  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));

  timeLog = rtc.now();

  // Visual indicator for setup completion
  digitalWrite(LED_BUILTIN, HIGH);

}

/*===========================================================================
 * Loop
 ===========================================================================*/
void loop() {
  if (timeLog == rtc.now()) {
    hertz_code();
    counter++;
  }
  else {
    Serial.print("Hertz rate: ");
    Serial.println(counter);
    timeLog = rtc.now();
    counter = 0;
  }
}

void hertz_code() {
  /* Put loop code to test here */
  
}