#include <SPI.h>                  // Built in
#include <SD.h>                   // Built in
#include <Wire.h>                 // Built in
#include <HX711.h>                // HX711 0.7.5 by Bogdan Necula
#include <RTClib.h>               // RTClib 2.0.2 by Adafruit. 
                                  // NOTE: Dependent on Adafruit BusIO 1.11.1 by Adafruit.
#include <Adafruit_BMP280.h>      // BMP280 2.6.1 by Adafruit. 
                                  // NOTE: Dependent on Adafruit Unified Sensor 1.1.4 by Adafruit.

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>


void setup(void) 
{
  Serial.begin(115200);

  if (!SD.begin(10)) {
    Serial.println("Card failed, or not present");
  }

  File dataFile = SD.open("datalog.txt", FILE_WRITE);
  if (SD.exists("datalog.txt")) {
    Serial.println("Writing to the file!");
    dataFile.print("Hi ");
  }
  else {
     Serial.println("No, it didn't work");
  }

  dataFile.close();
}

void loop(void) 
{
  File dataFile = SD.open("datalog.txt", FILE_WRITE);
  if (SD.exists("datalog.txt")) {
    Serial.println("Writing to the file!");
    dataFile.print("Hi ");
  }
  else {
     Serial.println("No, it didn't work");
  }

  dataFile.close();
}