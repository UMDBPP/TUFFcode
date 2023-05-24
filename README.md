<p align="center">
    <img src="https://user-images.githubusercontent.com/32310846/161163001-b1b6c3a0-91b8-45e9-89de-cac2818c7562.png"  width="500" />
</p>

# Launch: 10/16/2022 🎈
Arduino code for _TUFF DOS_ payload for the Balloon Payload Program at the University of Maryland. The payload reads tension data from the rope in atmospheric balloon launches (>50,000 ft).

Code by Jeremy Kuznetsov, Jim Oliver Villegas, Jaxon Lee, and Malcolm Maas.

<p align="center">
    <img src="https://user-images.githubusercontent.com/32310846/197653943-cb48b95a-080f-4381-9ff6-abcb2744c0a2.jpeg"  width="1000" />
</p>

-------

## Quickstart 🚀
```
sudo snap install arduino
git clone https://github.com/UMDBPP/TUFFcode
```
OR...

1. Download [Arduino IDE](https://www.arduino.cc/en/software)
2. Download [TUFF_Flight_Data_Collector.ino](TUFF_Flight_Data_Collector/TUFF_Flight_Data_Collector.ino) (or copy paste)
4. Run [TUFF_Flight_Data_Collector.ino](TUFF_Flight_Data_Collector/TUFF_Flight_Data_Collector.ino) with payload hanging load free 
5. You're ready to launch!

Note: Run TUFF_calibration with its experiment procedure for more accurate readings


## Code Structure 📁
The code is broken up as follows:

- [📁](Data%20Analysis)`Data Analysis`: Python Juypter Notebook analysis of TUFF data
    - [📁](Data%20Analysis/Data)`Data`: All data collected across our 4 flights. Includes formatted and unformatted data
    - [🏃](Data%20Analysis/TUFF_DOS_112_ANAL.py)`*.py`: Files with analysis. Run them to see graphs of our data 
- [🏃](Launch_Day_Tester/Launch_Day_Tester.ino)`Launch_Day_Tester/Launch_Day_Tester.ino`: Extra file to put various tests in
- [🏃](TUFF_Calibrator/TUFF_Calibrator.ino)`TUFF_Calibrator/TUFF_Calibrator.ino`: Gets calibration value for tension sensor. See file for details
- [🏃](TUFF_Flight_Data_Collector/TUFF_Flight_Data_Collector.ino)`TUFF_Flight_Data_Collector/TUFF_Flight_Data_Collector.ino`: Collects data during flight and writes to an SD card


# Specs 🔌
- [High Accuracy S-Beam Load Cell](https://www.omega.com/en-us/force-strain-measurement/load-cells/lc103b/p/LC103B-25): ±0.005 lbs
- [HX711 Amplifier](https://www.amazon.com/SparkFun-Load-Cell-Amplifier-HX711/dp/B079LVMC6X/ref=sr_1_1?crid=31PAXOZCNWVAN&keywords=sparkfun+hx711&qid=1648232977&sprefix=sparkfun+hx711%2Caps%2C80&sr=8-1)
- [Adafruit 9-DOF Gyro Sensor and Accelerometer](https://www.adafruit.com/product/2472)
- [Adafruit BMP280 Sensor](https://www.adafruit.com/product/2651)
- [RTC_DS1307 Clock](https://www.adafruit.com/product/3296)
- [Arduino Uno](https://store-usa.arduino.cc/products/arduino-uno-rev3)
- 16 GB SD Card
- SD Card Reader
- 9 Volt battery

<p align="center">
    <img src="https://user-images.githubusercontent.com/32310846/197654118-b540db57-1fec-4d6f-9f25-5f9d3cf12ee3.jpeg"  width="1000" />
</p>

# Preceding Flights ⏪!

- TUFF 105          Nov 14,     2021
- TUFF 110          Mar 5,      2022
- TUFF DOS 111      July 31,    2022
- TUFF DOS 112      Oct 16,     2022

