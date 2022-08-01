#!/usr/bin/env python
# coding: utf-8
# 
# This program analyzes TUFF DOS Payload data. The first half works the
# data into a usable form. The second half analyzes the data.
# Intial analysis--
# Average HZ: 31.83
# Ascent / Descent Tension:  ___ / ___
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
        
read_file.plot(x ='Time', y='Tension', kind = 'line')
plt.ylim(-10, 25)

read_file.plot(x ='Time', y='Altitude', kind = 'line')

# In[]
# Find ascent rate. Use linear algebra and get "m" 
# (gradient of line of best fit)
df = read_file[150000:200000]
df['ones']=1
A = df[['Time','ones']]
y = df['Altitude']
m, c = np.linalg.lstsq(A,y)[0]



# In[265]:
# Get rid of junk values from before and after launch
# Start index: 93542 (2166 seconds, 10:14:47)
# End index: 287140 (8497 seconds, 12:00:17)
# Balloon "popped": 228088  --> 134546 f/ new_df (6272 seconds, 11:23:12)

new_df = read_file[93541:287140]


# In[274]:
#---------------------------------
# BEGIN DATA ANALYSIS
# Tension, Altitude, and Temperature

z = np.linspace(0, 10, 1000)
new_df.plot(x ='Time', y={'Tension'}, kind = 'line')
new_df.plot(x ='Time', y={'Altitude'}, kind = 'line')
new_df.plot(x ='Time', y={'Temperature'}, kind = 'line')


# In[238]:
# Variance
"""
from scipy.io.wavfile import write
from scipy.fft import fft, fftfreq

N = 231615
SAMPLE_RATE = 12

yf = fft(np.array(read_file['Tension']))
xf = fftfreq(N, 1 / SAMPLE_RATE)

write("TUFF_WAV.wav", SAMPLE_RATE, np.array(read_file['Tension']))

plt.xlim((-0.002, 0.002))
plt.plot(xf, np.abs(yf))
plt.show()
"""

# In[ ]:
new_df['Variance2'] = new_df['Tension'].rolling(1000).var()

variance_plot = new_df.plot(x ='Time', y='Variance2', kind = 'line')
alt_plot = new_df.plot(x ='Time', y='Altitude', kind = 'line', ax = variance_plot, secondary_y = True)

variance_plot.set_ylabel('Variance')
alt_plot.set_ylabel('Altitude')

x = new_df['Time'].to_numpy()
y = new_df['Altitude'].to_numpy()


# In[ ]:

# The index of the balloon pop.
POP_POINT = 134546

weight = 8.576236354
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
drag_plot.axvline(x = 2645.5, color = 'red', linestyle = 'dashed')
drag_plot.axvline(x = 6027.818181818182, color = 'red', linestyle = 'dashed')

# Find average drag at different points
drag_df['Average_drag'] = new_df['Drag'].rolling(500).mean()

# Plot average drag against altitude
drag_plot = drag_df.plot(x = 'Time', y = 'Average_drag', kind = 'line')
drag_df.plot(x ='Time', y='Altitude', kind = 'line', ax = drag_plot, secondary_y = True)

# Put lines where jet stream begins and ends
drag_plot.axvline(x = 2645.5, color = 'red', linestyle = 'dashed')
drag_plot.axvline(x = 6027.818181818182, color = 'red', linestyle = 'dashed')

# %%
