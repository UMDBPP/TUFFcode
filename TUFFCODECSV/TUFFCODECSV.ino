/*===========================================================================
 * T.U.F.F (Tension Under Flight Forces) UMD BPP In-Flight Code
 * By Jeremy Kuznetsov, Jim Oliver Villegas, Jaxon Lee
 * 
 * This keeps track of tension data on BPP balloon launches using a load cell.
 ===========================================================================*/

// Libraries
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


// Misc Defining
#define CS 10 // Chip Select on SD logger
#define ledPin 9 // LED


// Declaring Objects
HX711 loadcell;
RTC_DS1307 rtc;
Adafruit_BNO055 bno = Adafruit_BNO055(55);
Adafruit_BMP280 bmp;
Adafruit_Sensor *bmp_temp = bmp.getTemperatureSensor();
Adafruit_Sensor *bmp_pressure = bmp.getPressureSensor();



// Wiring for the HX711 Amplifier
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;



// Loadcell calibration values. Calibrated to our load cell particularly.
// Offset - "zeroing the loadcell"
// Divider - "converting amp readings to lbs"
const long LOADCELL_OFFSET = 50682624;
const long LOADCELL_DIVIDER = 27451.29667; 

// Variables
float tension = 0;  // Tension sensor data
DateTime timelog;   // Timestamp data
float pressure = 0; // Measured in Pascals.
float bmptemp = 0;  // Measured in degrees Celsius.
float alt = 0;      // Measured in meters.
sensors_vec_t abs_orientation;
sensors_vec_t acceleration;
sensors_vec_t magnometer;

// Constant
const float sealevelpressure = 1017.25; //hPa of local sea level pressure, I assume?


/*===========================================================================
 * Setup
 ===========================================================================*/

void setup() {
  // MAKE SURE TO SET THE BAUD RATE IN VSCODE TO 9600
  Serial.begin(115200);

  Serial.println("BEGIN IN-FLIGHT CODE");
  //----------------------------

  // SD Card Test
  Serial.print("Initializing SD card...");

  if (!SD.begin(CS)) {
    Serial.println("Card failed, or not present");
  }
  else {
    Serial.println("card initialized.");
  }
//--------------------------
  
  // Initialize HX711 (load cell) with pinning/offsets/calibration
  loadcell.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN); 
  loadcell.set_offset(LOADCELL_OFFSET);  
  loadcell.set_scale(LOADCELL_DIVIDER);

  // Zero scale
  loadcell.tare(10);

  /* Initialise the Gyro/Accelerometer/Magnometer sensor */
  if(!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
  }
  
  delay(1000);
    
  bno.setExtCrystalUse(true);
//--------------------------

  // Alert user if RTC fails to open.
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    delay(10);
  }

  // Ensures rtc begins.
  rtc.begin();
  
  // Set RTC Date/Time. This only needs to be run once EVER.
  // rtc.adjust(DateTime(F(__DATE__), F(__TIME__))); 

//-------------------------

  // Alert user if the BMP sensor fails to open.
  if (!bmp.begin()) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring or "
                      "try a different address!"));
  }

  // Ensures the BMP sensor begins.
  bmp.begin();

  

  Serial.print("START LOOP OF IN-FLIGHT CODE");
  //-------------------------
  pinMode(ledPin, OUTPUT); // Declare LED as an output pin
}

/*===========================================================================
 * Loop
 ===========================================================================*/
void loop() {
  int i;
  // To write to a file with this SD logger, you must first open the file
  File dataFile = SD.open("datalog.txt", FILE_WRITE);

  for (i = 0; i < 10; i++) {

    
    //----------------------
    // Attempt to get reading from loadcell, retry if failed
    tension = loadcell.get_units(1);

    //---------------------
    // Get reading from RTC
    timelog = rtc.now();

  //--------------------
    // Get BMP readings
    bmptemp = bmp.readTemperature();
    pressure = bmp.readPressure();
    alt = bmp.readAltitude(sealevelpressure);
  //--------------------
  #if false
    /* Get BNO sensor "event" (it's readings) */ 
    sensors_event_t event; 
    bno.getEvent(&event, Adafruit_BNO055::VECTOR_EULER);
    abs_orientation = event.orientation;
    
    bno.getEvent(&event, Adafruit_BNO055::VECTOR_ACCELEROMETER);
    acceleration = event.acceleration;

    bno.getEvent(&event, Adafruit_BNO055::VECTOR_MAGNETOMETER);
    magnometer = event.magnetic;

    /* Display the floating point data */
    Serial.print("gX: ");
    Serial.print(abs_orientation.x, 4);
    Serial.print("\tgY: ");
    Serial.print(abs_orientation.y, 4);
    Serial.print("\tgZ: ");
    Serial.print(abs_orientation.z, 4);
    Serial.println("");

    Serial.print("aX: ");
    Serial.print(acceleration.x, 4);
    Serial.print("\taY: ");
    Serial.print(acceleration.y, 4);
    Serial.print("\taZ: ");
    Serial.print(acceleration.z, 4);
    Serial.println("");


    Serial.print("mX: ");
    Serial.print(magnometer.x, 4);
    Serial.print("\tmY: ");
    Serial.print(magnometer.y, 4);
    Serial.print("\tmZ: ");
    Serial.print(magnometer.z, 4);
    Serial.println("");

    Serial.println("");
    #endif
    // ==========Writing Data==========

    

    // If the file is available (meaning that it could open the file from the SD card), write to it:
    if (dataFile) {

      // Timestamp Data
      dataFile.print(timelog.year(), DEC); dataFile.print("/"); dataFile.print(timelog.month(), DEC); dataFile.print("/"); dataFile.print(timelog.day(), DEC); dataFile.print("|"); 
      dataFile.print(timelog.hour(), DEC); dataFile.print(":"); dataFile.print(timelog.minute(), DEC); dataFile.print(":"); dataFile.print(timelog.second(), DEC);
      dataFile.print(",");


      // Tension Data
      dataFile.print(tension);
      dataFile.print(",");

      // BMP Data
      dataFile.print(bmptemp);
      dataFile.print(",");
      dataFile.print(pressure);
      dataFile.print(",");
      dataFile.print(alt);
      dataFile.print(",");

/*
      // BNO 9-Axis data
      dataFile.print(abs_orientation.x);
      dataFile.print(",");
      dataFile.print(abs_orientation.y);
      dataFile.print(",");
      dataFile.print(abs_orientation.z);
      dataFile.print(",");

      dataFile.print(acceleration.x);
      dataFile.print(",");
      dataFile.print(acceleration.y);
      dataFile.print(",");
      dataFile.print(acceleration.z);
      dataFile.print(",");

      dataFile.print(magnometer.x);
      dataFile.print(",");
      dataFile.print(magnometer.y);
      dataFile.print(",");
      dataFile.print(magnometer.z);
      dataFile.print(",");

*/

      

      dataFile.println();

    }
    
    else {
      //Serial.println("error opening datalog.txt");
    }
  }
  dataFile.close();
  
  /*
//==================Serial Monitoring============
    // Tension Data
    Serial.print("Tension: "); Serial.print(tension); Serial.print(" lbs");
    Serial.print(',');
    Serial.println();   
    */ 
    
}