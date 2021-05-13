# read segy
import numpy as np
from scipy.signal import butter, lfilter, filtfilt, welch
import matplotlib.pyplot as plt
from segpy.reader import create_reader

segy_filename_haniya = r'.\\data_files\\vibe_sweep\\Haniya-GF-SGY\\210426_03.sgy'
segy_filename_lekhwair = r'.\\data_files\\vibe_sweep\\Lekhwair-GF-SGY\\local_200225_03.sgy'
print(segy_filename_haniya)
dt = 4 / 1000 # sampling interval is 4 ms
df = 1 / dt # sampling frequency
lowcut = 0.5
highcut = 100.0
pi = np.pi
sweep_length = 9000 # ms
max_lag = 129
FIGSIZE = (12, 8)



def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def zerophase_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def plot_gf(ax, segy_filename, pilot_trace, endian='>', color='black'):
    with open(segy_filename, 'rb') as segy_file:
        seg_y_dataset = create_reader(segy_file, endian=endian)
        for trace_number in range(seg_y_dataset.num_traces()):
            time_ms = []
            sample_val = []
            for i, val in enumerate(seg_y_dataset.trace_samples(trace_number)):
                time_ms.append(i * int(1000 * dt))
                sample_val.append(float(val))

            ax[trace_number].plot(time_ms, sample_val, color=color)

            if trace_number == pilot_trace:
                pilot = list(zip(time_ms, sample_val))

    return pilot

ax1 = [None]*4
fig1, (ax1[0], ax1[1], ax1[2], ax1[3]) = plt.subplots(nrows=4, ncols=1, figsize=FIGSIZE)
pilot_1 = plot_gf(ax1, segy_filename_haniya, 0, endian='<', color='black')
fig1.suptitle('GF Haniya')
fig1.subplots_adjust(hspace=0.4)
ax1[0].set_title('pilot')
ax1[1].set_title('mass')
ax1[2].set_title('baseplate')
ax1[3].set_title('GF')

ax2 = [None]*4
fig2, (ax2[0], ax2[1], ax2[2], ax2[3]) = plt.subplots(nrows=4, ncols=1, figsize=FIGSIZE)
pilot_2 = plot_gf(ax2, segy_filename_lekhwair, 3, endian='>', color='red')
fig2.suptitle('GF Lekhwair')
fig2.subplots_adjust(hspace=0.4)
ax2[0].set_title('GF')
ax2[1].set_title('baseplate')
ax2[2].set_title('mass')
ax2[3].set_title('pilot')

ax3 = [None]*2
fig3, (ax3[0], ax3[1]) = plt.subplots(nrows=2, ncols=1, figsize=FIGSIZE)
fig3.suptitle('Pilot comparison Haniya - Lekhwair')
fig3.subplots_adjust(hspace=0.4)
ax3[0].set_title('Pilot')
ax3[1].set_title('Power spectrum')

pilot_time = np.array(list(map(lambda x: x[0], pilot_1)))

pilot_1_vals = np.array(list(map(lambda x: x[1], pilot_1)))
# pilot_1_vals = zerophase_filter(pilot_1_vals, lowcut, highcut, df)
pilot_1_vals /= max(pilot_1_vals)

pilot_2_vals = np.array(list(map(lambda x: x[1], pilot_2)))
# pilot_2_vals = zerophase_filter(pilot_2_vals, lowcut, highcut, df)
pilot_2_vals /= max(pilot_2_vals)

pilot_len = min(pilot_1_vals.size, pilot_2_vals.size)
ax3[0].plot(pilot_time[:pilot_len], pilot_1_vals[:pilot_len],
            color='black', label='Haniya')
ax3[0].plot(pilot_time[:pilot_len], pilot_2_vals[:pilot_len],
            color='red', label='Lekhwair')
handles, labels = ax3[0].get_legend_handles_labels()
ax3[0].legend(
    handles, labels, loc='best', frameon=False,
    fontsize='small', framealpha=1, markerscale=40)

f, pilot_1_ps = welch(pilot_1_vals, df) # scaling='spectrum')
# ax3[1].plot(f, 10*np.log10(pilot_1_ps), color='black')
ax3[1].semilogy(f, pilot_1_ps, color='black')
f, pilot_2_ps = welch(pilot_2_vals, df) # scaling='spectrum')
# ax3[1].plot(f, 10*np.log10(pilot_2_ps), color='red')
ax3[1].semilogy(f, pilot_2_ps, color='red')
# ax3[1].set_ylim(0.5e-12, 0)

# calculate cross correlation - not plotted
corr_function = np.correlate(pilot_1_vals, pilot_2_vals, mode='full') / pilot_len
corr_function = corr_function[(pilot_len-1) - (max_lag - 1):(pilot_len - 1) + max_lag]
time_lags = np.arange(-(max_lag - 1), max_lag)

plt.tight_layout()
plt.show()
