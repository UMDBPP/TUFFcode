#!/usr/bin/env python
# coding: utf-8
# 
# This program analyzes TUFF DOS Payload data. The first half works the
# data into a usable form. The second half analyzes the data.
# Intial analysis--
# Average HZ: 31.83
# Ascent / Descent Tension:  4.84 lbs / 5.24 lbs
# Everything below TUFF: ~5.22 lbs
# Ascent Rate: 5.67 m/s
#
# Code written by Oliver Villegas and Jaxon Lee.



# In[110]:
# Get everything set up
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Define constant file name
OG_DATA_LOG = 'DATALOG_7_31_DOS.TXT'

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
    seconds = int(sliced)
    
    # Subtract the first seconds value from all seconds readings.
    if ('offset' not in locals()):
        offset = (3600 * hours) + (60 * minutes) + seconds
    raw_sec = ((3600 * hours) + (60 * minutes) + seconds) - offset
        
    
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
# Start index: 93542 (2166 seconds, 10:14:47)
# End index: 287140 (8497 seconds, 12:00:17)
# Balloon "popped": 228088  --> 134546 f/ new_df (6272 seconds, 11:23:12)

new_df = read_file[93541:287140]

# 88301 93547
# In[274]:
#---------------------------------
# BEGIN DATA ANALYSIS
# Tension, Altitude, and Temperature

# Just Tension
new_df.plot(x ='Time', y='Tension', kind = 'line')

# Tension and altitude
tension_plot = new_df.plot(x ='Time', y='Tension', kind = 'line')
new_df.plot(x ='Time', y='Altitude', kind = 'line', ax = tension_plot, 
            secondary_y = True)

# Temperature 
new_df.plot(x ='Time', y='Temperature', kind = 'line')

# In[]:
# Average Tension

# Find average tension at different points
new_df['Average_tension'] = new_df['Tension'].rolling(500).mean()

# Plot average tension and altitude
tension_plot = new_df.plot(x ='Time', y ='Average_tension', kind = 'line')
new_df.plot(x ='Time', y='Altitude', kind = 'line', ax = tension_plot, 
            secondary_y = True)

# In[]:
# Gyro and Accelerometer
# The data for angle x and angle z are essentially unreadable in this form.

# The index of the balloon pop.
POP_POINT = 134546

start_index = new_df.index[0]
accel_outliers = np.where(new_df['AccelerationZ'] == 0)[0]
accel_outliers += start_index
imu_df = new_df.copy()

# Remove outliers
imu_df.drop(accel_outliers, inplace = True)


imu_df.plot(x = 'Time', y = 'AccelerationZ', kind = 'line')
print("Average up/down acceleration: " + str(imu_df['AccelerationZ'][:POP_POINT].mean()))

# In[238]:
# Fast Fourier Transformation
# Applies a fast fourier transform to a slice of Tension data.

from scipy.fft import rfft, rfftfreq

# Input the number of seconds you wish to test over and what the start time is.
# Data starts around 2168 seconds.
seconds = 20
start_time = 4000


# Samples is seconds * average_hz.
SAMPLES = seconds *  32

# Find the index corresponding to the START_TIME
START_INDEX = np.where(new_df['Time'] == start_time)[0][0]

# Find the hertz rate of this slice
time_array = new_df['Time'][START_INDEX:SAMPLES + START_INDEX].to_numpy()
SAMPLE_RATE = len(time_array) / (time_array[-1] - time_array[0])
SAMPLE_RATE = int(SAMPLE_RATE)  # Convert to int.

# Apply real Fast Fourier Transform (real FFT) to the data. Take a slice of
# data with "SAMPLES" number of data points. Zero the mean to improve
# result quality.
yf = rfft(np.array(new_df['Average_tension'][START_INDEX:SAMPLES + START_INDEX]
                   -new_df['Average_tension'][START_INDEX:SAMPLES + START_INDEX]
                   .mean()))
xf = rfftfreq(SAMPLES, 1 / SAMPLE_RATE)


plt.xlim((0, 3))
plt.plot(xf, np.abs(yf))
plt.show()

# Analysis:
# There seems to be a spike around 0.16 hz.

# In[ ]:
# Variance
new_df['Variance'] = new_df['Tension'].rolling(1000).var()

variance_plot = new_df.plot(x ='Time', y='Variance', kind = 'line')
alt_plot = new_df.plot(x ='Time', y='Altitude', kind = 'line', ax = variance_plot, secondary_y = True)

variance_plot.set_ylabel('Variance')
alt_plot.set_ylabel('Altitude')

x = new_df['Time'].to_numpy()
y = new_df['Altitude'].to_numpy()

# 3 Spikes: 
# 1. 16499.35 km at index 195534 (5158 seconds)
# 2. 17563.90 km at index 201939 (5371.8 seconds)
# 3. 20919.24 km at index 134544 (6272.5 seconds)

# The 3rd spike is probably the balloon pop at max altitude.

# In[ ]:



weight = 5.22
weight_array_a = np.full([POP_POINT], weight)
weight_array_d = np.full([len(new_df) - POP_POINT], weight)
array_of_ascent_tension = new_df[:POP_POINT]['Tension']
array_of_descent_tension = new_df[POP_POINT:]['Tension']

# Performs weight arithmetic
drag_ascent = np.subtract(array_of_ascent_tension.to_numpy(), weight_array_a)
drag_descent = np.subtract(weight_array_d, array_of_descent_tension.to_numpy())


# Concatenates drags
drag = np.concatenate((drag_ascent, drag_descent))

new_df['Drag'] = drag

new_df.plot(x = 'Time', y = 'Drag', kind = 'line')

FINAL_DATA = new_df
new_df.to_csv('CSV_TUFF_DOS.CSV', index='Time')

# In[ ]:
drag_df = new_df

# Plot drag against altitude
drag_plot = drag_df.plot(x = 'Time', y = 'Drag', kind = 'line')
drag_df.plot(x ='Time', y='Altitude', kind = 'line', ax = drag_plot, secondary_y = True)

# Put lines where jet stream begins and ends
time_8k = np.where(drag_df['Altitude'] > 8000)[0][0] + drag_df.index[0]
time_15k = np.where(drag_df['Altitude'] > 15000)[0][0] + drag_df.index[0]

drag_plot.axvline(x = drag_df['Time'][time_8k], color = 'red', linestyle = 'dashed')
drag_plot.axvline(x = drag_df['Time'][time_15k], color = 'red', linestyle = 'dashed')

# Find average drag at different points
drag_df['Average_drag'] = new_df['Drag'].rolling(500).mean()

# Plot average drag against altitude
drag_plot = drag_df.plot(x = 'Time', y = 'Average_drag', kind = 'line')
drag_df.plot(x ='Time', y='Altitude', kind = 'line', ax = drag_plot, secondary_y = True)

# Put lines where jet stream begins and ends
drag_plot.axvline(x = drag_df['Time'][time_8k], color = 'red', linestyle = 'dashed')
drag_plot.axvline(x = drag_df['Time'][time_15k], color = 'red', linestyle = 'dashed')


# In[]
# Find ascent rate. Use linear algebra and get "m" 
# (gradient of line ot fit)f bes
ascent_df = new_df[:21706]
ascent_df['ones']=1
A = ascent_df[['Time','ones']]
y = ascent_df['Altitude']
m, c = np.linalg.lstsq(A,y)[0]

print("Ascent rate: " + str(m))

descent_df = new_df[180578:]
descent_df['ones']=1
A = descent_df[['Time','ones']]
y = descent_df['Altitude']
m, c = np.linalg.lstsq(A,y)[0]

print("Descent rate: " + str(m))

# %%
