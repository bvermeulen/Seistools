
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

quantum_response_file = Path('./data_files/quantum_zero_phase.csv')
dt = 4/1000      # sampling interval is 4 ms
df = 1/dt        # sampling frequency
pi = np.pi
max_display_frequency = 135 # Hz
phase_display = (-200, 10) # radians
max_samples = 256

quantum_response_df = pd.read_csv(quantum_response_file)
quantum_response_df['time'] = quantum_response_df['time'] * 0.001

# padding of the dataframe to max_samples
time_ = quantum_response_df.iloc[-1]['time'] + dt * 1000
for sample in range(int(quantum_response_df.iloc[-1]['sample'])+1, max_samples + 1):
    quantum_response_df = quantum_response_df.append({'sample':sample, 'time':time_, 'value':0.0}, ignore_index=True)
    time_ += dt * 1000

print(quantum_response_df.head())

time = quantum_response_df['time']
response_values = quantum_response_df['value']
fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(8, 7))
ax[0].set_xlim(-100, 100)
ax[0].set_title('filter response')
ax[0].plot(time, response_values)

ax[1].set_title('power spectrum')
ax[1].set_xlim(0, max_display_frequency)
scale = 'dB'
ax[1].magnitude_spectrum(response_values, Fs=df, scale=scale)

ax[2].set_title('phase')
ax[2].set_ylim(phase_display[0], phase_display[1])
ax[2].set_xlim(0, max_display_frequency)
# get the phase spectrum values and frequencies values;
# plot invisible and use a non default color
phase_values, freq, _ = ax[2].phase_spectrum(
    response_values, Fs=df, visible=True, color='red')

# check for modulus pi to keep values between -pi and pi
phase_values = np.mod(phase_values, pi)
ax[2].plot(freq, phase_values)

plt.tight_layout()
plt.show()

