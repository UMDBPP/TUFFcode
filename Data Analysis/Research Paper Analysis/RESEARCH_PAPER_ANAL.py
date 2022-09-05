#!/usr/bin/env python
# coding: utf-8
# 
# This program analyzes TUFF 110 and TUFF DOS 111 for use in 
# Code written by Jeremy Kuznetsov, Oliver Villegas, and Jaxon Lee.


# In[110]:
# Get everything set up
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


# Set pyplot preferences
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

tuff_110_df = pd.read_csv('CSV_TUFF_110.CSV')
tuff_dos_df = pd.read_csv('CSV_TUFF_DOS.CSV')


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
print("Average up acceleration: " + str(imu_df['AccelerationZ'][:83908].mean()))
print("Average down acceleration: " + str(imu_df['AccelerationZ'][-3000:-500].mean()))

imu_df['Average_accelerationZ'] = imu_df['AccelerationZ'].rolling(500).mean()
imu_df.plot(x = 'Time', y = 'Average_accelerationZ', kind = 'line')

# In[ ]:
# Calculate drag

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
# Calculate average drag

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

# Get tensions above 10,000 ft (convert m to ft)
above_10k_ft = np.where(new_df['Altitude'] >= 10000 * 0.3048)[0]
first_10k = above_10k_ft[0]
second_10k = above_10k_ft[-1]

ascent_tension = new_df['Tension'][1000:first_10k].mean()
descent_tension = new_df['Tension'][second_10k:-1000].mean()

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
ascent_df = new_df[1500:first_10k].copy()
ascent_df['ones'] = 1
A = ascent_df[['Time','ones']]
y = ascent_df['Altitude']
m, c = np.linalg.lstsq(A,y)[0]

print("Ascent rate: " + str(m))

descent_df = new_df[second_10k:-1000].copy()
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
START_TIME = 4000


# Samples is seconds * average_hz.
samples = SECONDS *  32

# Find the index corresponding to the START_TIME
start_index = np.where(new_df['Time'] == START_TIME)[0][0]

# Find the hertz rate of this slice
time_array = new_df['Time'][start_index:samples + start_index].to_numpy()
sample_rate = len(time_array) / (time_array[-1] - time_array[0])
sample_rate = int(sample_rate)  # Convert to int.

# Apply real Fast Fourier Transform (real FFT) to the data. Take a slice of
# data with "SAMPLES" number of data points. Zero the mean to improve
# result quality.
yf = rfft(np.array(new_df['Tension'][start_index:samples + start_index]
                   -new_df['Tension'][start_index:samples + start_index]
                   .mean()))
xf = rfftfreq(samples, 1 / sample_rate)



plt.xlim((0, 1))
plt.plot(xf, np.abs(yf))
plt.plot([0.135, 0.135], [-50, 400], 'k-', lw=2, color = 'red')
plt.show()


# Analysis:
# There seems to be a spike around 0.16 hz and a smaller spike around 0.64 hz.

# In[ ]:
# Variance
# This may tell us jetstream altitude locations. 
# Keep an eye on the "spikes" in tension variance.

new_df['Variance'] = new_df['Tension'].rolling(1000).var()

variance_plot = new_df.plot(x ='Time', y='Variance', kind = 'line')
alt_plot = new_df.plot(x ='Time', y='Altitude', kind = 'line', ax = variance_plot, secondary_y = True)

variance_plot.set_ylabel('Variance')
alt_plot.set_ylabel('Altitude')

x = new_df['Time'].to_numpy()
y = new_df['Altitude'].to_numpy()

# 3 Spikes: 
# 1. 16499.35 m at index 195534 (5158 seconds)
# 2. 17563.90 m at index 201939 (5371.8 seconds)
# 3. 20919.24 m at index 134544 (6272.5 seconds)

# The 3rd spike is probably the balloon pop at max altitude.
