#!/usr/bin/env python
# coding: utf-8
# 
# This program analyzes TUFF DOS Payload data. The first half works the
# data into a usable form. The second half analyzes the data.
# Conclusions:
#
# Code written by Oliver Villegas and Jaxon Lee.


# In[110]:
# Get everything set up
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Define constant file name
OG_DATA_LOG = 'Data/TUFF_DOS_112.TXT'

# Set pyplot preferences
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

# Put datalog data into a "CSV" file (spreadsheet)
headers = ['Time', 'Tension', 'Temperature', 'Pressure', 'Altitude', 'AngleX', 
           'AngleY', 'AngleZ', 'AccelerationX', 'AccelerationY', 
           'AccelerationZ', 'MagnometerX', 'MagnometerY', 'MagnometerZ']
read_file = pd.read_csv(OG_DATA_LOG, names=headers, index_col=False)


# In[113]:
# Remove data from "Time" values.

np_time = read_file['Time']
new_times = []

for time in np_time:
    new_times.append(time[(time.find("|") + 1):])

# In[183]:
# Get time in terms of seconds since launch.

raw_seconds = []

# Convert all hours/minutes to seconds
for time in new_times:
    hours = int(time[:(time.find(":"))])
    sliced = time[(time.find(":") + 1):]
    minutes = int(sliced[:(sliced.find(":"))])
    sliced = sliced[(sliced.find(":") + 1):]
    SECONDS = int(sliced)
    
    # Subtract the first seconds value from all seconds readings.
    if ('offset' not in locals()):
        offset = (3600 * hours) + (60 * minutes) + SECONDS
    raw_sec = ((3600 * hours) + (60 * minutes) + SECONDS) - offset
        
    
    raw_seconds.append(raw_sec)
    


# In[188]:
# Differentiate seconds of the same value. Assume every reading is equally
# spaced apart and adjust seconds values accordingly.

last_second = 0
sub_array = []
i = 1
j = 0
count = 1

for sec in range(len(raw_seconds) - 1):
    if raw_seconds[i] == raw_seconds[i - 1]:
        count = count + 1
    else:        
        if count > 0:
            decimal = 1/count
        else:
            decimal = 0
        while j < count:
            #print(count)
            raw_seconds[(i - count) + j] = raw_seconds[(i - count) + j] + (decimal * j)
            j = j + 1
            
        #Resets counters  
        count = 1  
        j = 0
        

    i = i + 1

# Set time to the ones we just calculated
read_file['Time'] = raw_seconds

# In[197]:
# Remove data spikes, referred to as "outliers".
read_file.plot(x ='Time', y='Tension', kind = 'line')
# Find outliers (values with a change of 4 lbs in 1/40th of a second)
outliers = []
for index in read_file.index.values.tolist():
    if (index < len(read_file) - 1):
        if (abs(read_file['Tension'][index] - read_file['Tension'][index + 1])
            > 4):
            outliers.append(index)
            
# Remove outliers
for outlier_index in outliers:
    i = 1
    # Find the nearest non-outlier.
    while ((outlier_index + i) in outliers):
        i += 1
    # Ensure we don't go over the array size.
    if (outlier_index + i < len(read_file['Tension'].to_numpy())):
        read_file['Tension'][outlier_index] = read_file['Tension'][outlier_index + i]





# In[265]:
# Get rid of junk values from before and after launch
# Start index: 328599 (8831 seconds)
# End index: 577965 (15056 seconds)
# Balloon "popped": 456464  --> 127865 f/ new_df (6272 seconds)

dos_112_df = read_file[328599:577965]

# A calibration weight was placed on TUFF DOS before the launch.
CALIBRATION_WEIGHT = 4.4236
MEASURED_WEIGHT = 3.91

# Adjust the tension values based on calibrated values 
dos_112_df['Tension'] *= CALIBRATION_WEIGHT / MEASURED_WEIGHT

# Convert altitude values from m into ft
dos_112_df['Altitude'] *= 3.28084


# In[274]:
#---------------------------------
# BEGIN DATA ANALYSIS
# Tension, Altitude, and Temperature

# Just Tension
dos_112_df.plot(x ='Time', y='Tension', kind = 'line')

# Graph Time vs. Tension
tension_plot = dos_112_df.plot(x = 'Time', y = 'Tension', kind = 'line', 
                 title = 'Time vs. Tension and Altitude')
alt_plot = dos_112_df.plot(x ='Time', y='Altitude', kind = 'line', xlabel = 'Time (seconds)', 
                 ax = tension_plot, secondary_y = True)

tension_plot.set_ylabel('Tension (lbs)')
alt_plot.set_ylabel('Altitude (ft)')

# Temperature 
dos_112_df.plot(x ='Time', y='Temperature', kind = 'line')

# In[]:
# Average Tension

# Find average tension at different points
dos_112_df['Average_tension'] = dos_112_df['Tension'].rolling(500).mean()

# Plot average tension and altitude
tension_plot = dos_112_df.plot(x = 'Time', y = 'Average_tension', kind = 'line', 
                 title = 'Time vs. Average Tension and Altitude')
alt_plot = dos_112_df.plot(x ='Time', y='Altitude', kind = 'line', xlabel = 'Time (seconds)', 
                 ax = tension_plot, secondary_y = True)

tension_plot.set_ylabel('Average Tension (lbs)')
alt_plot.set_ylabel('Altitude (ft)')



# In[]:
# Gyro and Accelerometer
# The data for angle x and angle z are essentially unreadable in this form.

# The index of the balloon pop.
POP_POINT = 127865

start_index = dos_112_df.index[0]
accel_outliers = np.where(dos_112_df['AccelerationZ'] == 0)[0]
accel_outliers += start_index
imu_df = dos_112_df.copy()

# Remove outliers
imu_df.drop(accel_outliers, inplace = True)

# Remove acceleration due to gravity
imu_df['AccelerationZ'] += 9.80057


imu_df.plot(x = 'Time', y = 'AccelerationZ', kind = 'line')
print("Average up acceleration: " + str(imu_df['AccelerationZ'][:83908].mean()))
print("Average down acceleration: " + str(imu_df['AccelerationZ'][-3000:-500].mean()))

imu_df['Average_accelerationZ'] = imu_df['AccelerationZ'].rolling(500).mean()
imu_df.plot(x = 'Time', y = 'Average_accelerationZ', kind = 'line')

# In[ ]:
# Calculate drag

weight = 3.8289
weight_array_a = np.full([POP_POINT], weight)
weight_array_d = np.full([len(dos_112_df) - POP_POINT], weight)
array_of_ascent_tension = dos_112_df[:POP_POINT]['Tension']
array_of_descent_tension = dos_112_df[POP_POINT:]['Tension']

# Performs weight arithmetic
drag_ascent = np.subtract(array_of_ascent_tension.to_numpy(), weight_array_a)
drag_descent = np.subtract(weight_array_d, array_of_descent_tension.to_numpy())


# Concatenates drags
drag = np.concatenate((drag_ascent, drag_descent))

dos_112_df['Drag'] = drag

dos_112_df.plot(x = 'Time', y = 'Drag', kind = 'line')

FINAL_DATA = dos_112_df
dos_112_df.to_csv('Data/CSV_TUFF_DOS_112.CSV', index='Time')

# In[ ]:
# Calculate average drag

drag_df = dos_112_df

# Plot drag against altitude
drag_plot = drag_df.plot(x = 'Time', y = 'Drag', kind = 'line')
drag_df.plot(x ='Time', y='Altitude', kind = 'line', ax = drag_plot, secondary_y = True)

# Put lines where jet stream begins and ends
time_8k = np.where(drag_df['Altitude'] > 8000)[0][0] + drag_df.index[0]
time_15k = np.where(drag_df['Altitude'] > 15000)[0][0] + drag_df.index[0]

drag_plot.axvline(x = drag_df['Time'][time_8k], color = 'red', linestyle = 'dashed')
drag_plot.axvline(x = drag_df['Time'][time_15k], color = 'red', linestyle = 'dashed')

# Find average drag at different points
drag_df['Average_drag'] = dos_112_df['Drag'].rolling(500).mean()

# Plot average drag against altitude
drag_plot = drag_df.plot(x = 'Time', y = 'Average_drag', kind = 'line')
drag_df.plot(x ='Time', y='Altitude', kind = 'line', ax = drag_plot, secondary_y = True)

# Put lines where jet stream begins and ends
#drag_plot.axvline(x = drag_df['Time'][time_8k], color = 'red', linestyle = 'dashed')
#drag_plot.axvline(x = drag_df['Time'][time_15k], color = 'red', linestyle = 'dashed')


# In[]
# Modified tension

# Correct for potential erroneous loadcell divider. Optimal: 32.70%
#new_df['Tension'] *= 1.3270
#tension_plot = new_df.plot(x ='Time', y='Tension', kind = 'line')
#new_df.plot(x ='Time', y='Altitude', kind = 'line', ax = tension_plot, 
#            secondary_y = True)


# In[]:
# Find ascent/descent tension (below 10,000 ft)

# Get tensions above 10,000 ft
above_10k_ft = np.where(dos_112_df['Altitude'] >= 10000)[0]
first_10k = above_10k_ft[0]
second_10k = above_10k_ft[-1]

ascent_tension = dos_112_df['Tension'][1000:first_10k].mean()
descent_tension = dos_112_df['Tension'][second_10k:-1000].mean()

print("Ascent tension: " + str(ascent_tension))
print("Descent tension: " + str(descent_tension))

# In[]

# First parameter is x, second parameter is y, and third parameter is degree
#fit = np.polyfit(new_df['Time'][:POP_POINT], new_df['Altitude'][:POP_POINT], 2)
#equation = np.poly1d(fit)
#print ("The fit coefficients are a = {0:.4f}, b = {1:.4f} c = {2:.4f}".format(*fit))
#print (equation)

# In[]
# Find ascent rate. Use linear algebra and get "m" 
# (gradient of line ot fit)f bes
ascent_df = dos_112_df[1500:first_10k].copy()
ascent_df['ones'] = 1
A = ascent_df[['Time','ones']]
y = ascent_df['Altitude']
m, c = np.linalg.lstsq(A,y)[0]

print("Ascent rate: " + str(m))

descent_df = dos_112_df[second_10k:-1000].copy()
descent_df['ones'] = 1
A = descent_df[['Time','ones']]
y = descent_df['Altitude']
m, c = np.linalg.lstsq(A,y)[0]

print("Descent rate: " + str(m))


# In[238]:
# Fast Fourier Transformation
# Applies a fast fourier transform to a slice of Tension data.
# This helps measure payload oscillations in hertz.

from scipy.fft import rfft, rfftfreq

# Input the number of seconds you wish to test over and what the start time is.
# Data starts around 2168 seconds.
SECONDS = 60
START_TIME = 9300


# Samples is seconds * average_hz.
samples = SECONDS *  32

# Find the index corresponding to the START_TIME
start_index = np.where(dos_112_df['Time'] == START_TIME)[0][0]

# Find the hertz rate of this slice
time_array = dos_112_df['Time'][start_index:samples + start_index].to_numpy()
sample_rate = len(time_array) / (time_array[-1] - time_array[0])
sample_rate = int(sample_rate)  # Convert to int.

# Apply real Fast Fourier Transform (real FFT) to the data. Take a slice of
# data with "SAMPLES" number of data points. Zero the mean to improve
# result quality.
yf = rfft(np.array(dos_112_df['Tension'][start_index:samples + start_index]
                   -dos_112_df['Tension'][start_index:samples + start_index]
                   .mean()))
xf = rfftfreq(samples, 1 / sample_rate)


plt.xlabel('Frequency (hz)')
plt.ylabel('Intensity')
plt.title('Fast Fourier transform of tension from the time space to the frequency space ')
plt.xlim((0, 1))
plt.plot(xf, np.abs(yf))
#plt.plot([0.3, 0.3], [-50, 1000], 'k-', lw=2, color = 'red')
plt.show()


# Analysis:
# There seems to be a spike around 0.16 hz and a smaller spike around 0.64 hz.

# In[ ]:
# Variance
# This may tell us jetstream altitude locations. 
# Keep an eye on the "spikes" in tension variance.

dos_112_df['Variance'] = dos_112_df['Tension'].rolling(1000).var()

variance_plot = dos_112_df.plot(x ='Time', y='Variance', kind = 'line',
                                 title = 'Variance and Altitude vs Time')
alt_plot = dos_112_df.plot(x ='Time', y='Altitude', kind = 'line', 
                            xlabel = 'Time (seconds)', ax = variance_plot, 
                            secondary_y = True)

variance_plot.set_ylabel('Variance (lbs^2)')
alt_plot.set_ylabel('Altitude (ft)')

# 1 Spike: 
# 1. 48986.88 ft at index 476299 (12436.475 seconds)

# There was no spike at the zenith because there was no balloon pop.

# In[ ]:
# Add your code here!

