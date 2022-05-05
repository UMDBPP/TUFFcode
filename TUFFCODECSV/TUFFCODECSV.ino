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

#include <Adafruit_10DOF.h>       // Adafruit 10DOF 1.1.1 by Adafruit

#include <Adafruit_AHRS_FusionInterface.h>
#include <Adafruit_AHRS_Madgwick.h>
#include <Adafruit_AHRS_Mahony.h>
#include <Adafruit_AHRS_NXPFusion.h>
#include <Adafruit_AHRS.h>
#include <Adafruit_Sensor_Set.h>
#include <Adafruit_Simple_AHRS.h>   // Adafruit AHRS 2.3.2 by Adafruit

#include <Adafruit_L3GD20_U.h>
#include <Adafruit_L3GD20.h>        // Adafruit L3GD20 2.0.1 by Adafruit



#include <Adafruit_LSM303_U.h>
#include <Adafruit_LSM303.h>        // Adafruit LSM303DLHC 1.0.4




// Misc Defining
#define CS 10 // Chip Select on SD logger
#define ledPin 9 // LED


// Declaring Objects
HX711 loadcell;
RTC_DS1307 rtc;
Adafruit_LSM303_Accel_Unified accel = Adafruit_LSM303_Accel_Unified(30301);
Adafruit_LSM303_Mag_Unified   mag   = Adafruit_LSM303_Mag_Unified(30302);
Adafruit_L3GD20_Unified       gyro  = Adafruit_L3GD20_Unified(20);
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
sensors_vec_t angular_momentum;
sensors_vec_t linear_acceleration;
sensors_vec_t magnometer_measurement;

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

  /* Initialise the sensors */
  if(!accel.begin())
  {
    /* There was a problem detecting the ADXL345 ... check your connections */
    Serial.println(F("Ooops, no LSM303 detected ... Check your wiring!"));
  }
  if(!mag.begin())
  {
    /* There was a problem detecting the LSM303 ... check your connections */
    Serial.println("Ooops, no LSM303 detected ... Check your wiring!");
  }
  if(!gyro.begin())
  {
    /* There was a problem detecting the L3GD20 ... check your connections */
    Serial.print("Ooops, no L3GD20 detected ... Check your wiring or I2C ADDR!");
  }

  Serial.print("START LOOP OF IN-FLIGHT CODE");
  //-------------------------
  pinMode(ledPin, OUTPUT); // Declare LED as an output pin
}

/*===========================================================================
 * Loop
 ===========================================================================*/
void loop() {

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
  // Get gyro/accelerometer readings
  sensors_event_t event;

  /* Get the results (gyrocope values in rad/s) */
  gyro.getEvent(&event);
  angular_momentum = event.gyro;

  /* Get the results (acceleration is measured in m/s^2) */
  accel.getEvent(&event);
  linear_acceleration = event.acceleration;

  /* Get the results (magnetic vector values are in micro-Tesla (uT)) */
  mag.getEvent(&event);
  magnometer_measurement = event.magnetic;


// ==========Writing Data==========

  // To write to a file with this SD logger, you must first open the file
  File dataFile = SD.open("datalog.txt", FILE_WRITE);

  // If the file is available (meaning that it could open the file from the SD card), write to it:
  if (dataFile) {

    //Timestamp Data
    dataFile.print(timelog.year(), DEC); dataFile.print("/"); dataFile.print(timelog.month(), DEC); dataFile.print("/"); dataFile.print(timelog.day(), DEC); dataFile.print("|"); 
    dataFile.print(timelog.hour(), DEC); dataFile.print(":"); dataFile.print(timelog.minute(), DEC); dataFile.print(":"); dataFile.print(timelog.second(), DEC);
    dataFile.print(",");


    //Tension Data
    dataFile.print(tension);
    dataFile.print(",");

    //BMP Data
    dataFile.print(bmptemp);
    dataFile.print(",");
    dataFile.print(pressure);
    dataFile.print(",");
    dataFile.print(alt);
    dataFile.print(",");

    // Gyro Data
    dataFile.print(angular_momentum.x);
    dataFile.print(",");
    dataFile.print(angular_momentum.y);
    dataFile.print(",");
    dataFile.print(angular_momentum.z);
    dataFile.print(",");

    // Accelerometer Data
    dataFile.print(linear_acceleration.x);
    dataFile.print(",");
    dataFile.print(linear_acceleration.y);
    dataFile.print(",");
    dataFile.print(linear_acceleration.z);
    dataFile.print(",");

    // Magnometer Data
    dataFile.print(magnometer_measurement.x);
    dataFile.print(",");
    dataFile.print(magnometer_measurement.y);
    dataFile.print(",");
    dataFile.print(magnometer_measurement.z);
    dataFile.print(",");

    

    dataFile.println();

    dataFile.close();
  }
  
  else {
    Serial.println("error opening datalog.txt");
  }
  /*
//==================Serial Monitoring============
    // Tension Data
    Serial.print("Tension: "); Serial.print(tension); Serial.print(" lbs");
    Serial.print(',');
    Serial.println();    
    */
}