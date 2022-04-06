#include <MPU6050_tockn.h>
#include <Wire.h>

MPU6050 mpu6050(Wire);

void setup() {
  Serial.begin(9600);
  Wire.begin();
  mpu6050.begin();
  mpu6050.calcGyroOffsets(true);
}

void loop() {
  mpu6050.update();
  Serial.print("angleX : ");
  Serial.print(mpu6050.getAngleX());
  Serial.print("\tangleY : ");
  Serial.print(mpu6050.getAngleY());
  Serial.print("\tangleZ : ");
  Serial.println(mpu6050.getAngleZ());
}

#if false
#include <GY521.h>     // GY521 version 0.3.5 by Rob Tillaart.
GY521 gyro(0x68);

//
//    FILE: GY521_pitch_roll_yaw.ino
//  AUTHOR: Rob Tillaart
// PURPOSE: demo pitch roll yaw
//    DATE: 2020-08-06

uint32_t counter = 0;

void setup()
{
  Serial.begin(9600);
  Serial.println("Yoo");
  Serial.println(__FILE__);

  Wire.begin();
  gyro.begin();

  delay(100);
  while (gyro.wakeup() == false)
  {
    Serial.print(millis());
    Serial.println("\tCould not connect to GY521");
    delay(1000);
  }
  gyro.setAccelSensitivity(2);  // 8g
  gyro.setGyroSensitivity(1);   // 500 degrees/s

  gyro.setThrottle();
  Serial.println("start...");

  // set calibration values from calibration sketch.
  gyro.axe = 0;
  gyro.aye = 0;
  gyro.aze = 0;
  gyro.gxe = 0;
  gyro.gye = 0;
  gyro.gze = 0;
}


void loop()
{
  gyro.read();
  float pitch = gyro.getPitch();
  float roll  = gyro.getRoll();
  float yaw   = gyro.getYaw();

  if (counter % 10 == 0)
  {
    Serial.println("\nCNT\tPITCH\tROLL\tYAW");
  }

  Serial.print(counter);
  Serial.print('\t');
  Serial.print(pitch, 3);
  Serial.print('\t');
  Serial.print(roll, 3);
  Serial.print('\t');
  Serial.print(yaw, 3);
  Serial.println();

  counter++;
}


// -- END OF FILE --


#endif
// COPIED FROM https://electrosome.com/interfacing-mpu-6050-gy-521-arduino-uno/
#if false
#include <Wire.h>
#include <math.h> //library includes mathematical functions

const int MPU=0x68; //I2C address of the MPU-6050
int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ; //16-bit integers
int AcXcal,AcYcal,AcZcal,GyXcal,GyYcal,GyZcal,tcal; //calibration variables
double t,tx,tf,pitch,roll;

void setup()
{
    Wire.begin(); //initiate wire library and I2C
    Wire.beginTransmission(MPU); //begin transmission to I2C slave device
    Wire.write(0x6B); // PWR_MGMT_1 register
    Wire.write(0); // set to zero (wakes up the MPU-6050)  
    Wire.endTransmission(true); //ends transmission to I2C slave device
    Serial.begin(9600); //serial communication at 9600 bauds
}

void loop()
{
    Wire.beginTransmission(MPU); //begin transmission to I2C slave device
    Wire.write(0x3B); // starting with register 0x3B (ACCEL_XOUT_H)
    Wire.endTransmission(false); //restarts transmission to I2C slave device
    Wire.requestFrom(MPU,14,true); //request 14 registers in total  

    //Acceleration data correction
    AcXcal = -950;
    AcYcal = -300;
    AcZcal = 0;

    //Temperature correction
    tcal = -1600;

    //Gyro correction
    GyXcal = 480;
    GyYcal = 170;
    GyZcal = 210;


    //read accelerometer data
    AcX=Wire.read()<<8|Wire.read(); // 0x3B (ACCEL_XOUT_H) 0x3C (ACCEL_XOUT_L)  
    AcY=Wire.read()<<8|Wire.read(); // 0x3D (ACCEL_YOUT_H) 0x3E (ACCEL_YOUT_L) 
    AcZ=Wire.read()<<8|Wire.read(); // 0x3F (ACCEL_ZOUT_H) 0x40 (ACCEL_ZOUT_L)
  
    //read temperature data 
    Tmp=Wire.read()<<8|Wire.read(); // 0x41 (TEMP_OUT_H) 0x42 (TEMP_OUT_L) 
  
    //read gyroscope data
    GyX=Wire.read()<<8|Wire.read(); // 0x43 (GYRO_XOUT_H) 0x44 (GYRO_XOUT_L)
    GyY=Wire.read()<<8|Wire.read(); // 0x45 (GYRO_YOUT_H) 0x46 (GYRO_YOUT_L)
    GyZ=Wire.read()<<8|Wire.read(); // 0x47 (GYRO_ZOUT_H) 0x48 (GYRO_ZOUT_L) 

    //temperature calculation
    tx = Tmp + tcal;
    t = tx/340 + 36.53; //equation for temperature in degrees C from datasheet
    tf = (t * 9/5) + 32; //fahrenheit

    //get pitch/roll
    getAngle(AcX,AcY,AcZ);
  
    //printing values to serial port
    Serial.print("Angle: ");
    Serial.print("Pitch = "); Serial.print(pitch);
    Serial.print(" Roll = "); Serial.println(roll);
  
    Serial.print("Accelerometer: ");
    Serial.print("X = "); Serial.print(AcX + AcXcal);
    Serial.print(" Y = "); Serial.print(AcY + AcYcal);
    Serial.print(" Z = "); Serial.println(AcZ + AcZcal); 

    Serial.print("Temperature in celsius = "); Serial.print(t);  
    Serial.print(" fahrenheit = "); Serial.println(tf);  
  
    Serial.print("Gyroscope: ");
    Serial.print("X = "); Serial.print(GyX + GyXcal);
    Serial.print(" Y = "); Serial.print(GyY + GyYcal);
    Serial.print(" Z = "); Serial.println(GyZ + GyZcal);
  
    delay(1000);
}

//function to convert accelerometer values into pitch and roll
void getAngle(int Ax,int Ay,int Az) 
{
    double x = Ax;
    double y = Ay;
    double z = Az;

    pitch = atan(x/sqrt((y*y) + (z*z))); //pitch calculation
    roll = atan(y/sqrt((x*x) + (z*z))); //roll calculation

    //converting radians into degrees
    pitch = pitch * (180.0/3.14);
    roll = roll * (180.0/3.14) ;
}
#endif

#if false
//
//    FILE: readCalibration.ino
//  AUTHOR: Rob Tillaart
// PURPOSE: read the calibration values / errors for a flat sensor.
//    DATE: 2020-07-14


#include "GY521.h"

GY521 sensor(0x69);

uint32_t counter = 0;

float ax, ay, az;
float gx, gy, gz;
float t;


void setup()
{
  Serial.begin(115200);
  Serial.println(__FILE__);

  Wire.begin();
  delay(100);
  if (sensor.wakeup() == false)
  {
    Serial.println("Could not conect to GY521");
  }
  // adjust when needed.
  sensor.setAccelSensitivity(0);  // 2g
  sensor.setGyroSensitivity(0);   // 250 degrees/s
  sensor.setThrottle(false);

  // set all calibration errors to zero
  sensor.axe = 0;
  sensor.aye = 0;
  sensor.aze = 0;
  sensor.gxe = 0;
  sensor.gye = 0;
  sensor.gze = 0;

  Serial.println("\n\nReading calibration numbers...");
}


void loop()
{
  ax = ay = az = 0;
  gx = gy = gz = 0;
  t = 0;
  for (int i = 0; i < 20; i++)
  {
    sensor.read();
    ax -= sensor.getAccelX();
    ay -= sensor.getAccelY();
    az -= sensor.getAccelZ();
    gx -= sensor.getGyroX();
    gy -= sensor.getGyroY();
    gz -= sensor.getGyroZ();
    t += sensor.getTemperature();
  }

  if (counter % 10 == 0)
  {
    Serial.println("\n\tACCELEROMETER\t\tGYROSCOPE\t\tTEMPERATURE");
    Serial.print('\t');
    Serial.print(sensor.axe, 3);
    Serial.print('\t');
    Serial.print(sensor.aye, 3);
    Serial.print('\t');
    Serial.print(sensor.aze, 3);
    Serial.print('\t');
    Serial.print(sensor.gxe, 3);
    Serial.print('\t');
    Serial.print(sensor.gye, 3);
    Serial.print('\t');
    Serial.print(sensor.gze, 3);
    Serial.print('\n');
    Serial.println("\taxe\taye\taze\tgxe\tgye\tgze\tT");
  }

  Serial.print(counter);
  Serial.print('\t');
  Serial.print(ax * 0.05, 3);
  Serial.print('\t');
  Serial.print(ay * 0.05, 3);
  Serial.print('\t');
  Serial.print(az * 0.05, 3);
  Serial.print('\t');
  Serial.print(gx * 0.05, 3);
  Serial.print('\t');
  Serial.print(gy * 0.05, 3);
  Serial.print('\t');
  Serial.print(gz * 0.05, 3);
  Serial.print('\t');
  Serial.print(t * 0.05, 2);
  Serial.println();

  // adjust calibration errors so table should get all zero's.
  sensor.axe += ax * 0.05;
  sensor.aye += ay * 0.05;
  sensor.aze += az * 0.05;
  sensor.gxe += gx * 0.05;
  sensor.gye += gy * 0.05;
  sensor.gze += gz * 0.05;

  counter++;
  delay(100);
}


// -- END OF FILE --

#endif