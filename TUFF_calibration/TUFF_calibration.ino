/*===========================================================================
 * T.U.F.F (Tension Under Flight Forces) UMD BPP
 * Sensor calibration code
 * By Jeremy Kuznetsov and Jaxon Lee
 *
 * This code identifies the practical "scale" for the tension load cell.
 * The scale converts the load cell reading to human-readable measurements (lbs).
 * Specifically, the conversion works as follows:
 *  load_cell_measurement / SCALE = human_readable_measurement
 *
 * Procedure:
 *  1. Allow the sensor 5 seconds to "zero" itself before applying any weight
 *  2. Put known weight (~2 lbs) on the load cell
 *  3. Write down the value that results. Many numbers will pop out, so use
 *     your best judgement to find a general average
 *  4. Repeat steps 2. and 3. with increasing weight until 20 lbs is reached
 *  5. Input values into a spreadsheet. Graph the tension as "x" and the
 *     known weight as "y". Create a line of best fit and note the "m" in "mx+b".
 *     It should be a low value between 0 and  1 (ex. 0.00003).
 *  6. Assign the INVERSE (ex. 0.00003 ^-1 = 33,333) of this value to the 
 *     "LOADCELL_DIVIDER" variable in the in-flight source code (yes, you need 
 *     to hard code the value in).
 *  7. Profit :)
 ===========================================================================*/

// Libraries
#include <HX711.h>              // HX711 0.7.5 by Bogdan Necula
#include <Adafruit_BMP280.h>    // BMP280 2.6.1 by Adafruit. NOTE: Dependent on Adafruit Unified Sensor 1.1.4 by Adafruit


// Declaring load cell
HX711 loadcell;

// Wiring for the HX711 Amplifier
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

/*===========================================================================
 * Setup
 * Initialize the loadcell and prepare it for accurate readings.
 =========================================================================== */

void setup() {
  Serial.begin(9600);
  Serial.println("BEGIN CALIBRATION CODE");

  // Declare LED as an output pin and turn it off
  pinMode(LED_BUILTIN, OUTPUT); 
  digitalWrite(LED_BUILTIN, LOW);

  // Initialize HX711 with pinning.
  loadcell.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);  

  // Reset or "zero" loadcell readings.
  loadcell.set_scale();
  loadcell.tare(100);

  // Gives the load cell 1 second to ensure it finishes its startup
  Serial.println("Zeroing the load cell...");
  delay(1000);
  Serial.println("Load cell is zeroed and ready to go!");

  // Gives a visual indicator that the load cell is ready for calibration
  digitalWrite(LED_BUILTIN, HIGH);

}

/*===========================================================================
 * Loop
 * Spits out a value needed to calibrate the tension load cell.
 ===========================================================================*/
void loop() {

  // This averages the load cell's value across 250 readings.
  float tension = loadcell.get_value(250);

  Serial.print("Tension: ");
  Serial.println(tension);
  delay(100);
}