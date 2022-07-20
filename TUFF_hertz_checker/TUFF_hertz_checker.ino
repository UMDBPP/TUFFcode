/*===========================================================================
 * T.U.F.F (Tension Under Flight Forces) UMD BPP 
 * Hertz rate checker
 * By Jeremy Kuznetsov and Jaxon Lee
 * 
 * This program tests the hertz rate of SDFat. It runs the SD card for 5 seconds
 * and prints out how fast it was able to write.
 * 
 ===========================================================================*/

// Libraries
#include "SdFat.h"                // SdFat 2.1.2 by Bill Greiman
#include <SPI.h>                  // Built in
#include <Wire.h>                 // Built in
#include <HX711.h>                // HX711 0.7.5 by Bogdan Necula

// SDFat's verion of SD object
SdFat SD;

HX711 loadcell;

// Wiring for the HX711 Amplifier
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

// Loadcell calibration values. Calibrated to our load cell particularly.
// Offset - "zeroing the loadcell"
// Divider - "converting amp readings to lbs"
const long LOADCELL_OFFSET = 50682624;
const long LOADCELL_DIVIDER = 27451.29667; 


const int chipSelect = 8;
File experimentFile;
File readableFile;

struct datastore {
  float tension;
};

float tension = 0;  // Tension sensor data
int counter = 0;    // Number of readings
int total_Time;     // Total run time
long millis_at_start;



void setup() {
  // Initiliaze Arduino. Setting pin 10 to be an output pin is required.
  Serial.begin(115200);
  pinMode(10, OUTPUT);

  // Initialize HX711 (load cell) with pinning/offsets/calibration
  loadcell.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN); 
  loadcell.set_offset(LOADCELL_OFFSET);  
  loadcell.set_scale(LOADCELL_DIVIDER);

  // Zero scale
  loadcell.tare(10);

  // Try opening SD card until it works (up to 10 times).
  for (int i = 0; i < 10; i++){
    if (SD.begin(chipSelect)) {
      break;
    }
    else {
      Serial.print("Card failed, or not present. Trying again...--");
      Serial.println(i);
    }
  }

  // Remove old data from experiment files.
  SD.remove("fastlogging.txt");
  SD.remove("flightdata.txt");
  experimentFile = SD.open("fastlogging.txt", FILE_WRITE);
}


void loop() {
  // Go for 5 seconds.
  if (millis() - millis_at_start <= 5000) {
    // EXPERIMENT: Store as much data as possible in 5 seconds.
    // This part needs to be as fast as possible
    struct datastore myData;
    tension = loadcell.get_units(1);
    myData.tension = tension;
    Serial.print("myData.tension: ");
    Serial.println(myData.tension); 

  
    experimentFile.write((const uint8_t *)&myData, sizeof(myData));
    counter++;
  }
  // After 5 seconds, stop logging data
  // For this part logging time isn't important as all data allready has been stored
  else {
    Serial.println("END DEBUGGING.");
    total_Time = millis() - millis_at_start;
    experimentFile.close();
    experimentFile = SD.open("fastlogging.txt", FILE_READ);
    

    // Read data from "fastlogging.txt" and store it as CSV in "flightdata.txt"
    if (experimentFile.available()) {
      Serial.println("Reading experiment data...");
      struct datastore myData;
      readableFile = SD.open("flightdata.txt", FILE_WRITE);

      for (int i = 0; i < counter; i++) {
        experimentFile.read((uint8_t *)&myData, sizeof(myData));
        readableFile.print("Tension: ");
        readableFile.println(myData.tension);
      }
        Serial.println("Finished reading experiment data.");


    }

    Serial.println();
    Serial.print("Total time: ");
    Serial.println(total_Time);
    Serial.println("Hertz:");
    Serial.println(counter / 5);

    experimentFile.close();
    readableFile.close();

    // Hang the program.
    while (1);
  }
}

