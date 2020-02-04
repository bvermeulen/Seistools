import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from segpy.reader import create_reader

file_min_phase = 'himin.sgy'
file_zero_phase = 'hilin.sgy'
earth_model = [(500, +1.0), (1000, -0.5),
               (1200, +0.6), (2000, +0.2),
               (2100, -0.3), (2600, -0.2)]
noise_factor = 0.2
# earth_model = [(1000, +1.0)]

dt = 4       # sampling interval is 4 ms
df = 1 / dt  # sampling frequency
pi = np.pi
record_length = 4000  # ms

fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(8, 7))

with open(file_min_phase, 'rb') as segy_file:
    seg_y_dataset = create_reader(segy_file)

    pilot_samples = []
    for i, val in enumerate(seg_y_dataset.trace_samples(3)):
        pilot_samples.append((i * dt, val))

pilot_min_df = pd.DataFrame(pilot_samples, columns=['Time', 'Amplitude'])
pilot_min_trace = pilot_min_df['Amplitude']

with open(file_zero_phase, 'rb') as segy_file:
    seg_y_dataset = create_reader(segy_file)

    pilot_samples = []
    for i, val in enumerate(seg_y_dataset.trace_samples(3)):
        pilot_samples.append((i * dt, val))

pilot_zero_df = pd.DataFrame(pilot_samples, columns=['Time', 'Amplitude'])
pilot_zero_trace = pilot_zero_df['Amplitude']

earth_trace = [[i * dt, noise_factor * (0.5 - np.random.random_sample())]
               for i in range(int(record_length * df))]
for (t, val) in earth_model:
    earth_trace[int(t * df)][1] += val

earth_df = pd.DataFrame(earth_trace, columns=['Time', 'Amplitude'])

time = earth_df['Time']
earth_trace = earth_df['Amplitude']
ax[0].set_title('Earth')
ax[0].set_xlim(0, 17000)
ax[0].plot(time, earth_trace)

time = pilot_min_df['Time']
ax[1].set_title('Pilot')
ax[1].set_xlim(0, 17000)
ax[1].plot(time, pilot_min_trace)

convolved_trace = np.convolve(earth_trace, pilot_min_trace)
time = [(i * dt) for i in range(len(convolved_trace))]
ax[2].set_title('Convolved trace')
ax[2].set_xlim(0, 17000)
ax[2].plot(time, convolved_trace)

scaling = len(pilot_min_trace) * len(pilot_min_trace) * dt * dt * np.max(pilot_min_trace)
correlated_trace = np.correlate(convolved_trace, pilot_min_trace) / scaling
time = [(i * dt) for i in range(len(correlated_trace))]
ax[3].set_title('correlated')
ax[3].set_xlim(0, 17000)
ax[3].plot(time, correlated_trace)

plt.tight_layout()
plt.show()
