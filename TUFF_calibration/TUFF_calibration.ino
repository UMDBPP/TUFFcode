/*===========================================================================
 * T.U.F.F (Tension Under Flight Forces) UMD BPP 
 * Sensor calibration code
 * By Jeremy Kuznetsov and Jaxon Lee
 ===========================================================================*/

// Librariess
#include <HX711.h>              // HX711 0.7.5 by Bogdan Necula
#include <SPI.h>                // Built in
#include <SD.h>                 // Built in
#include <Wire.h>               // Built in
#include <RTClib.h>             // RTClib 2.0.2 by Adafruit. 
                                // NOTE: Dependent on BusIO 1.11.1 by Adafruit.
#include <Adafruit_BMP280.h>    // BMP280 2.6.1 by Adafruit. 
                                // NOTE: Dependent on Adafruit Unified Sensor 1.1.4 by Adafruit.


// Misc Defining
#define ONE_WIRE_BUS 8 // Temperature probe data line
#define CS 10 // Chip Select on SD logger
#define ledPin 9 // LED


// Declaring Objects
HX711 loadcell;
RTC_DS1307 rtc;
Adafruit_BMP280 bmp;
Adafruit_Sensor *bmp_temp = bmp.getTemperatureSensor();
Adafruit_Sensor *bmp_pressure = bmp.getPressureSensor();

// Wiring for the HX711 Amplifier
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

// Constants: Offsets for Load Cell Calibration
const long LOADCELL_OFFSET = 50682624;
const long LOADCELL_DIVIDER = 30000; //This is measured to calibrate our cell specifically

// Variables
float tension = 0;  // Tension sensor data
DateTime timelog;   // Timestamp data
float temp = 0;     // TempSensor Data
float pressure = 0;
float bmptemp = 0;
float alt = 0;
int counter = 0;

// Constant
const float sealevelpressure = 1017.25; //hPa of local sea level pressure, I assume?


/*===========================================================================
 * Setup
 =========================================================================== */

void setup() {
  Serial.begin(9600);
  Serial.println("BEGIN CALIBRATION CODE");
  pinMode(LED_BUILTIN, OUTPUT); // Declare LED as an output pin
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);

  // Initialize HX711 with pinning.
  loadcell.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);  

  // Reset or "zero" loadcell readings.
  loadcell.set_scale();
  loadcell.tare();

  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("Zeroing the load cell...");
  delay(5000);
  Serial.println("Load cell is zeroed and ready to go!");

  digitalWrite(LED_BUILTIN, HIGH);

}

/*===========================================================================
 * Loop
 ===========================================================================*/
void loop() {
  float known_weight = 1;
  float divider_scale = loadcell.get_units(50) / known_weight;
  Serial.print("Divider scale: ");
  Serial.println(divider_scale);
  delay(100);
}