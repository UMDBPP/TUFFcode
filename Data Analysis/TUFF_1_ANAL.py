#!/usr/bin/env python
# coding: utf-8

# In[110]:

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

# Put datalog data into a "CSV" file (spreadsheet)
headers = ['Time', 'Tension', 'Temperature', 'Pressure', 'Altitude']
read_file = pd.read_csv('Data/TUFF_DATA110.TXT', names=headers, index_col=False)

# In[130]:
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

read_file.plot(x ='Time', y='Tension', kind = 'line')


# In[265]:
# Get rid of junk values from before and after launch

#new_df = read_file
new_df = read_file[15500:80000]  # TUFF 110

# In[274]:
# Tension, Altitude, and Temperature

z = np.linspace(0, 10, 1000)
new_df.plot(x ='Time', y={'Tension'}, kind = 'line', title = 'Time vs. Tension', 
            xlabel = 'Time (seconds)', ylabel = 'Tension (lbs)')
new_df.plot(x ='Time', y={'Altitude'}, kind = 'line')
new_df.plot(x ='Time', y={'Temperature'}, kind = 'line')

tension_plot = new_df.plot(x ='Time', y='Tension', kind = 'line')
new_df.plot(x ='Time', y='Altitude', kind = 'line', ax = tension_plot, 
            secondary_y = True)

# In[]:
# Average Tension
# Find average tension at different points
new_df['Average_tension'] = new_df['Tension'].rolling(int(500/3)).mean()

# Plot average tension and altitude
tension_plot = new_df.plot(x ='Time', y='Average_tension', kind = 'line')
new_df.plot(x ='Time', y='Altitude', kind = 'line', ax = tension_plot, 
            secondary_y = True)

# In[238]:
# Variance

new_df['Variance2'] = new_df['Tension'].rolling(1000).var()

variance_plot = new_df.plot(x ='Time', y='Variance2', kind = 'line')
alt_plot = new_df.plot(x ='Time', y='Altitude', kind = 'line', ax = variance_plot, secondary_y = True)

variance_plot.set_ylabel('Variance')
alt_plot.set_ylabel('Altitude')

x = new_df['Time'].to_numpy()
y = new_df['Altitude'].to_numpy()
print("Rough estimate: " + str(np.interp(3700, x,y)))


print("Ascent/Descent value: " + str(np.where(new_df['Altitude'].to_numpy() 
                                              == max(new_df['Altitude']))))

# In[ ]:
weight = 8.576236354

array_of_ascent_tension = new_df[:39571]['Tension']
array_of_descent_tension = new_df[39571:]['Tension']
weight_array_a = np.full(len(array_of_ascent_tension), weight)
weight_array_d = np.full(len(array_of_descent_tension), weight)

# Performs weight arithmetic
drag_ascent = np.subtract(array_of_ascent_tension.to_numpy(), weight_array_a)
drag_descent = np.subtract(weight_array_d, array_of_descent_tension.to_numpy())


# Concatenates drags
drag = np.concatenate((drag_ascent, drag_descent))

new_df['Drag'] = drag

new_df.plot(x = 'Time', y = 'Drag', kind = 'line')


# Only consider values of for below 10,000 m
ten_thousand_cutoffs = np.where(abs(new_df['Altitude'].to_numpy() - 10000) <= 10)
df = pd.concat([new_df[:17934], new_df[49131:]])

FINAL_DATA = df

# In[ ]:
drag_df = df

# Plot drag against altitude
drag_plot = drag_df.plot(x = 'Time', y = 'Drag', kind = 'line')
drag_df.plot(x ='Time', y='Altitude', kind = 'line', ax = drag_plot, secondary_y = True)

# Put lines where jet stream begins and ends
drag_plot.axvline(x = 2645.5, color = 'red', linestyle = 'dashed')
drag_plot.axvline(x = 6027.818181818182, color = 'red', linestyle = 'dashed')

# Find average drag at different points
drag_df['Average_drag'] = df['Drag'].rolling(500).mean()

# Plot average drag against altitude
drag_plot = drag_df.plot(x = 'Time', y = 'Average_drag', kind = 'line')
drag_df.plot(x ='Time', y='Altitude', kind = 'line', ax = drag_plot, secondary_y = True)

# Put lines where jet stream begins and ends
drag_plot.axvline(x = 2645.5, color = 'red', linestyle = 'dashed')
drag_plot.axvline(x = 6027.818181818182, color = 'red', linestyle = 'dashed')



# In[ ]:
"""

import tensorflow as tf
import numpy as np
from numpy import array
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
import math
from sklearn.metrics import mean_squared_error
import os

ML_df = []
train_data = []
test_data = []
X_train = []
X_test = []
Y_train = []
Y_test = []
model = Sequential()
"""
