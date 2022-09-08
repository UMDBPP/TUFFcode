#!/usr/bin/env python
# coding: utf-8
# 
# This program analyzes TUFF 110 and TUFF DOS 111 for use in our research paper.
# "TUFF_NUMS" spreadsheet
# https://docs.google.com/spreadsheets/d/12MzcHWLXqzLgLZ56cs3QEGbjPwlLi2tpHEkvx9lI1uc/edit#gid=0
# Code written by Jeremy Kuznetsov, Oliver Villegas, and Jaxon Lee.


# In[1]:
# Get everything set up
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


# Set pyplot preferences
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

tuff_110_df = pd.read_csv('CSV_TUFF_110.CSV')
tuff_dos_df = pd.read_csv('CSV_TUFF_DOS.CSV')

#Convert altitude values from m into ft
tuff_110_df['Altitude'] *= 3.28084
tuff_dos_df['Altitude'] *= 3.28084


# BEGIN TUFF 110 ANALYSIS
#In[]:
# ----------- Tension -----------
# The flightline tension that TUFF  measured throughout the flight.
# What does Avg. Tension mean?
#   Assume: avg. tension is the same as simply the tension when no swinging
#           i.e. avg tension = "resting" tension
#           Swinging will cause increased tension?
#   Does Avg tension increase as oscillation rate increases? YES :(
#   
# 

# Graph Time vs. Tension
tension_plot = tuff_110_df.plot(x = 'Time', y = 'Tension', kind = 'line', 
                 title = 'Time vs. Tension and Altitude')
alt_plot = tuff_110_df.plot(x ='Time', y='Altitude', kind = 'line', xlabel = 'Time (seconds)', 
                 ax = tension_plot, secondary_y = True)

tension_plot.set_ylabel('Tension (lbs)')
alt_plot.set_ylabel('Altitude (ft)')

# Add red line
tuff_110_df['Average_tension'] = tuff_110_df['Tension'].rolling(1000).mean()
tuff_110_df.plot(x ='Time', y='Average_tension', kind = 'line', xlabel = 'Time (seconds)', 
                 ax = tension_plot, color = 'red')

#In[]:
# ----------- Basic Stats -----------
# The ascent and descent rate of TUFF 110.

# Get tensions above 10,000 ft
above_10k_ft = np.where(tuff_110_df['Altitude'] >= 10000)[0]
first_10k = above_10k_ft[0]
second_10k = above_10k_ft[-1]

ascent_tension = tuff_110_df['Tension'][100:first_10k].mean()
descent_tension = tuff_110_df['Tension'][second_10k:-100].mean()

print("Ascent tension: " + str(ascent_tension))
print("Descent tension: " + str(descent_tension))

ascent_df = tuff_110_df[:first_10k].copy()
ascent_df['ones'] = 1
A = ascent_df[['Time','ones']]
y = ascent_df['Altitude']
m, c = np.linalg.lstsq(A,y)[0]

print("Ascent rate: " + str(m))

descent_df = tuff_110_df[second_10k:].copy()
descent_df['ones'] = 1
A = descent_df[['Time','ones']]
y = descent_df['Altitude']
m, c = np.linalg.lstsq(A,y)[0]

print("Descent rate: " + str(m))

#In[]:
# ----------- Drag -----------
# The drag below TUFF that TUFF calculates using measurements throughout the flight.
WEIGHT_UNDER_TUFF = 8.576236354
POP_POINT_110 = np.where(tuff_110_df['Altitude'] == tuff_110_df['Altitude'].max())[0][0]

array_of_ascent_tension = tuff_110_df[:POP_POINT_110]['Tension'].copy()
array_of_ascent_tension -= WEIGHT_UNDER_TUFF


array_of_descent_tension = tuff_110_df[POP_POINT_110:]['Tension'].copy()
array_of_descent_tension -= WEIGHT_UNDER_TUFF
array_of_descent_tension *= -1


# Concatenates drags
drag = np.concatenate((array_of_ascent_tension, array_of_descent_tension))

tuff_110_df['Drag'] = drag

tuff_110_df.plot(x = 'Time', y = 'Drag', kind = 'line')
tuff_110_df['Average_drag'] = tuff_110_df['Drag'].rolling(1000).mean()
tuff_110_df.plot(x = 'Time', y = 'Average_drag', kind = 'line')


#In[]:
# ----------- Oscillations -----------
# The oscillation rate of the payload line.

#In[]:
# ----------- Variance -----------
# The variance of the tension data during the TUFF DOS launch



# ^^^^^^^ TUFF 110
# ==============================================================================
# ==============================================================================
# ==============================================================================
# vvvvvvv TUFF DOS
# BEGIN TUFF DOS ANALYSIS

#In[]:
# ----------- Tension -----------
# The flightline tension that TUFF DOS measured throughout the flight.

# Graph Time vs. Tension
tuff_dos_df.plot(x = 'Time', y = 'Tension', kind = 'line', 
                title = 'Time vs. Tension', ylabel = 'Tension (lbs)', 
                 xlabel = 'Time (seconds)')
tuff_dos_df.plot(x ='Time', y='Altitude', kind = 'line', ax = tension_plot, 
            secondary_y = True, ylabel= 'Altitude (ft)')

#In[]:
# ----------- Drag -----------
# The drag below TUFF that TUFF DOS calculates using measurements throughout the flight.


#In[]:
# Choppy Altitude
choppy_df = pd.read_csv("ns111a_take2.CSV")
choppy_df.plot(x = 'Time (s)', y = 'Alt (m)', kind = 'line', title = 'Altitude vs Time')

choppy_alt = pd.DataFrame()
choppy_alt['Time'] = choppy_df['Time (s)']
choppy_alt['Altitude'] = choppy_df['Alt (m)']

# Convert from m to ft.
choppy_alt['Altitude'] *= 3.28084


# Correct the time values
choppy_alt['Time'] -= 3109.4333333333334

myPlot = choppy_alt.plot(x = 'Time', y = 'Altitude', kind = 'line')
tuff_dos_df.plot(x ='Time', y='Altitude', kind = 'line', ax = myPlot, 
            secondary_y = False, ylabel= 'Altitude (ft)')


# TUFF DOS start        : 2167.162162162162
# TUFF DOS peak         : 6272.566666666667
# TUFF DOS end          : 8496.954545454546
# TUFF DOS Ascent Time  : 4105.4045
# TUFF DOS Descent Time : 2224.38788
# TUFF DOS total time   : 6329.792383292384

# Choppy start          : 5203 sec
# Choppy peak           : 9382 sec
# Choppy end            : 11782 sec
# Choppy enters 10k     : 6825  sec
# Choppy leaves 10k     : 10331 sec
# Choppy from 0 - 10k   : 1622 sec
# Choppy from 10k - 0   : 1451 sec
# Choppy ascent rate    : 6.1652 m/s
# Choppy descent rate   : 6.8918 m/s
# Choppy ascent time    : 4179 sec
# Choppy descent time   : 2400 sec
# Choppy total time     : 6579
# Choppy peak height    : 68632.6793616
# Choppy ascent rate 

# ----------- Basic Stats -----------
# The ascent and descent rate of TUFF DOS.
POP_POINT_DOS = 134546 # np.where(tuff_dos_df['Altitude'] == tuff_dos_df['Altitude'].max())[0][0] + 



# Get tensions above 10,000 ft
above_10k_ft = np.where(choppy_alt['Altitude'] >= 10000)[0]
first_10k = above_10k_ft[0]
second_10k = above_10k_ft[-1]

ascent_df_dos = choppy_alt[:first_10k].copy()
ascent_df_dos['ones'] = 1
A = ascent_df_dos[['Time','ones']]
y = ascent_df_dos['Altitude']
m, c = np.linalg.lstsq(A,y)[0]

print("Ascent rate: " + str(m))

descent_df_dos = choppy_alt[second_10k:].copy()
descent_df_dos['ones'] = 1
A = descent_df_dos[['Time','ones']]
y = descent_df_dos['Altitude']
m, c = np.linalg.lstsq(A,y)[0]

print("Descent rate: " + str(m))



#In[]:
# ----------- Oscillations -----------
# The oscillation rate of the Axient Payload, the one below TUFF DOS.

#In[]:
# ----------- Variance -----------
# The variance of the tension data during the TUFF DOS launch
