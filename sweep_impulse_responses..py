import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.mlab import window_none
from segpy.reader import create_reader

file_name1 = 'himin.sgy'
file_name2 = 'hilin.sgy'
corr_file_name = 'hicut_corr.csv'
wavelet_file_name = 'wavelet.csv'
corr_wavelet_file_name = 'wavelet_corr.csv'
dt = 4/1000 # sampling interval is 4 ms
df = 1/dt # sampling frequency
pi = np.pi
sweep_length = 14000 # ms
max_lag = 129
max_display_frequency = 90 # Hz
phase_display = (-10, 10) # radians

with open(file_name1, 'rb') as segy_file:
    seg_y_dataset = create_reader(segy_file)

    pilot_samples = []
    for i, val in enumerate(seg_y_dataset.trace_samples(3)):
        pilot_samples.append((i * int(1000 * dt), float(val)))

with open(file_name2, 'rb') as segy_file:
    seg_y_dataset = create_reader(segy_file)

    gf_samples = []
    for i, val in enumerate(seg_y_dataset.trace_samples(3)):
        gf_samples.append((i * int(1000 * dt), float(val)))

pilot_df = pd.DataFrame(pilot_samples, columns=['Time', 'Amplitude'])
gf_df = pd.DataFrame(gf_samples, columns=['Time', 'Amplitude'])
time = pilot_df['Time']
pilot = pilot_df['Amplitude']
gf = gf_df['Amplitude']

fig, ax = plt.subplots(nrows=5, ncols=1, figsize=(8, 7))

ax[0].set_title('Pilot')
ax[0].set_xlim(0, sweep_length)
ax[0].plot(time, pilot)

ax[1].set_title('GF')
ax[1].set_xlim(0, sweep_length)
ax[1].plot(time, gf)

ax[2].set_title('correlation pilot with GF')
corr_function = np.correlate(pilot, gf, mode='full') / len(pilot)
corr_function = corr_function[(len(pilot)-1)-(max_lag-1):(len(pilot)-1)+max_lag]
time_lags = np.arange(-(max_lag-1), max_lag)

corr_function_df = pd.DataFrame(zip(time_lags, corr_function), columns=['Time', 'Values'])
corr_function_df.to_csv(corr_file_name, index=False)
ax[2].plot(time_lags, corr_function)

wavelet_df = corr_function_df[corr_function_df['Time'] >= 0]
wavelet_df.to_csv(wavelet_file_name, index=False)
wavelet_length = len(wavelet_df)
wavelet_values = wavelet_df['Values'].to_list()

ax[3].set_title('Minimum phase wavelet')
ax[3].plot(time[0:wavelet_length], wavelet_values)

corr_wavelet = np.correlate(wavelet_values, wavelet_values, mode='full') / wavelet_length
corr_wavelet = corr_wavelet[(wavelet_length-1)-(max_lag-1):(wavelet_length-1)+max_lag]
time_lags = np.arange(-(max_lag-1), max_lag)
ax[4].plot(time_lags, corr_wavelet)

corr_wavelet_df = pd.DataFrame(zip(time_lags, corr_wavelet), columns=['Time', 'Values'])
corr_wavelet_df.to_csv(corr_wavelet_file_name, index=False)

# ax[3].set_title('autocorrelation re-ordered')
# cf_reordered = np.concatenate((corr_function[max_lag-1:], corr_function[0:max_lag-1]))
# time_lags = np.arange(0, 2*max_lag-1)
# ax[3].plot(time_lags, cf_reordered)
# print(len(corr_function))
# print(len(cf_reordered))

# ax[3].set_title('magnitude')
# ax[3].set_xlim(0, max_display_frequency)
# scale = 'linear'  #  'dB' # or 'default'
# ax[3].magnitude_spectrum(corr_function, Fs=df, scale=scale, window=window_none)

# ax[4].set_title('phase')
# ax[4].set_ylim(phase_display[0], phase_display[1])
# ax[4].set_xlim(0, max_display_frequency)
# get the phase spectrum values and frequencies values;
# plot invisible and use a non default color
# cf_phase_values, cf_freq, _ = ax[4].phase_spectrum(
#     cf_reordered, Fs=df, window=window_none, visible=False, color='r')

# check for modulus 2*pi and keep values between -pi and pi
# cf_phase_values = np.mod(cf_phase_values, 2 * pi)
# cf_phase_values[cf_phase_values > pi] -= 2 * pi

# cf_phase_values -= 2 * pi
# ax[4].plot(cf_freq, cf_phase_values)

plt.tight_layout()
plt.show()
