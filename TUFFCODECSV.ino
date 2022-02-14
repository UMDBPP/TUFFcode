/*===========================================================================
 * T.U.F.F (Tension Under Flight Forces) UMD BPP In-Flight Code
 ===========================================================================*/

// Libraries
#include <HX711.h>              //HX711 by Bogdan Necula
#include <SPI.h>
#include <SD.h>
#include <Wire.h>               
#include <OneWire.h>            //OneWire by Paul Stroffregen
#include <DallasTemperature.h>  //DallasTemperature by Miles Burton
#include <RTClib.h>             //RTClib by Adafruit
#include <Adafruit_BMP280.h>    //BMP280 by Adafruit


//Misc Defining
#define ONE_WIRE_BUS 8 // Temperature probe data line
#define CS 10 // Chip Select on SD logger
#define ledPin 9 // LED


//Declaring Objects
HX711 loadcell;
RTC_DS1307 rtc;
//OneWire oneWire(ONE_WIRE_BUS);
//DallasTemperature tempS(&oneWire);
Adafruit_BMP280 bmp;
Adafruit_Sensor *bmp_temp = bmp.getTemperatureSensor();
Adafruit_Sensor *bmp_pressure = bmp.getPressureSensor();

//Wiring for the HX711 Amplifier
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

// Constants: Offsets for Load Cell Calibration
const long LOADCELL_OFFSET = 50682624;
const long LOADCELL_DIVIDER = 30000; //This is measured to calibrate our cell specifically

//Variables
float tension = 0; //Tension sensor data
DateTime timelog; //Timestamp data
float temp = 0; //TempSensor Data
float pressure = 0;
float bmptemp = 0;
float alt = 0;
int counter = 0;

// Constant
const float sealevelpressure = 1017.25; //hPa of local sea level pressure, I assume?


/*===========================================================================
 * Setup
 ===========================================================================*/

void setup() {
  Serial.begin(9600);

//----------------------------

 //SD Card Test
  Serial.print("Initializing SD card...");

  if (!SD.begin(CS)) {
    Serial.println("Card failed, or not present");
  }

  Serial.println("card initialized.");

//--------------------------
  
  //Initialize HX711 with pinning/offsets/calibration
  loadcell.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  loadcell.set_offset(LOADCELL_OFFSET);
  loadcell.set_scale(LOADCELL_DIVIDER);

  // Zero scale
  loadcell.tare();

//--------------------------

  //Wait for RTC to respond
  if(!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    while (1) delay(10);
  }

  rtc.begin();
  
  //Set RTC Date/Time
  rtc.adjust(DateTime(F(__DATE__), F(__TIME__))); 
  
//-------------------------

 // tempS.begin(); //DallasTemp

//-------------------------

  if (!bmp.begin()) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring or "
                      "try a different address!"));
    while (1) delay(10);
  }

  bmp.begin();

//-------------------------
  pinMode(ledPin, OUTPUT); // Declare LED as an output pin
}

/*===========================================================================
 * Loop
 ===========================================================================*/
void loop() {

//----------------------
  // Attempt to get reading from loadcell, retry if failed
  if (loadcell.wait_ready_retry(10)) {
    //Stores reading from loadcell
    tension = loadcell.get_units(10);
  }
  else {
    Serial.println("HX711 not found.");
  }
//---------------------
  // Get reading from RTC
  timelog = rtc.now();
//--------------------
  /* //Getting reading from temp sensor
  tempS.requestTemperatures();
  temp = tempS.getTempCByIndex(0);
  if(temp = DEVICE_DISCONNECTED_C){
    Serial.println("Could not read temperature data"); 
  }*/
//--------------------
  bmptemp = bmp.readTemperature();
  pressure = bmp.readPressure();
  alt = bmp.readAltitude(sealevelpressure);
//--------------------

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

    /*//Temprature data
    dataFile.print("Temp: "); dataFile.print(temp); dataFile.print(" C");
    dataFile.print(',');
    dataFile.println();*/

    //BMP Data
    dataFile.print(bmptemp);
    dataFile.print(",");
    dataFile.print(pressure);
    dataFile.print(",");
    dataFile.print(alt);
    dataFile.print(",");
    
    dataFile.println();

    dataFile.close();
  }
  
  else {
    Serial.println("error opening datalog.txt");
  }

//==================Serial Monitoring============
    Serial.print(timelog.year(), DEC); Serial.print("/"); Serial.print(timelog.month(), DEC); Serial.print("/"); Serial.print(timelog.day(), DEC); Serial.print(" | "); 
    Serial.print(timelog.hour(), DEC); Serial.print(":"); Serial.print(timelog.minute(), DEC); Serial.print(":"); Serial.print(timelog.second(), DEC);
    Serial.print(',');
    Serial.println();

    //Tension Data
    Serial.print("Tension: "); Serial.print(tension); Serial.print(" lbs");
    Serial.print(',');
    Serial.println();

    /*//Temprature data
    Serial.print("Temp: "); Serial.print(temp); Serial.print(" C");
    Serial.print(',');
    Serial.println();*/

    //BMP Data
    Serial.print("BaroTemp: "); Serial.print(bmptemp); Serial.print(" C");
    Serial.print(',');
    Serial.println();
    Serial.print("Pressure: "); Serial.print(pressure); Serial.print(" Pa");
    Serial.print(',');
    Serial.println();
    Serial.print("Altitude: "); Serial.print(alt); Serial.print(" m");
    Serial.print(',');
    Serial.println();

    //Formatting
    Serial.println("-------------");

  //LED Identifier for writing
  if (counter > 20)
  {
    ///
    
  }
  else if (counter > 10)
  {
    ///
    counter = 0;
  }
  
  counter++;
  digitalWrite(ledPin, HIGH); // turn on the led
  delay(100);

  digitalWrite(ledPin, LOW); // turn off the LED
  delay(100);
}
