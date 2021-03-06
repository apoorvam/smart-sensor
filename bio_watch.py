import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import scipy.fftpack
import scipy as sp
from scipy.stats import zscore
import pandas as pd
from scipy.signal import butter, filtfilt
from scipy import signal
import warnings
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")
style.use('ggplot')

# Source: https://archive.ics.uci.edu/ml/datasets/MHEALTH+Dataset
input_file_path = 'datasets/uic_dataset.csv'

sampling_frequency = 50
average_filter_window_duration_hr = int((1/7)*sampling_frequency)
average_filter_window_duration_br = int((40/60)*sampling_frequency)
T = 1/sampling_frequency
save_plots = True

def normalize(data):
  for i in range(0, 3):
    data[:,i] = sp.stats.zscore(data[:,i])
  return data

def apply_average_filter(data, window):
  for i in range(0, 3):
    data[:,i] = np.array(pd.Series(data[:,i]).rolling(window=window).mean())
  return data

def plot(data, title, plot_save_path):
  N = len(data)
  y = np.linspace(0, N/sampling_frequency, N)
  plt.plot(y, data)

  plt.title(title)
  plt.ylabel('ACCELERATION Ax (m/s^2)')
  plt.xlabel('TIME (s)')
  draw_plot(plot_save_path)
  plt.close()

def draw_plot(plot_save_path):
  if (save_plots):
    plt.savefig(plot_save_path)
  else:
    plt.draw()
    plt.pause(5)

def butter_bandpass(lowcut, highcut, fs, order):
  nyq = 0.5 * fs
  low = lowcut / nyq
  high = highcut / nyq
  b, a = butter(order, [low, high], btype='band')
  return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
  b, a = butter_bandpass(lowcut, highcut, fs, order)
  y = filtfilt(b, a, data)
  return y

def apply_bandpass_butterworth_filter(data, low_cutoff_freq, high_cutoff_freq):
  order = 2
  y = butter_bandpass_filter(data, low_cutoff_freq, high_cutoff_freq, sampling_frequency, order)
  return y

def aggregate_components(data):
  return np.array(list(map(lambda c: np.sqrt(np.sum(np.square(c))) , data)), dtype=np.float64)

def fft(acc_data, f_low, f_high, plot_save_path):
  acc_data = acc_data[~np.isnan(acc_data)]
  acc_data = sp.signal.detrend(acc_data)
  N = len(acc_data)

  fft_data = sp.fftpack.fft(acc_data)
  f = np.linspace(0, N/sampling_frequency, N)

  plt.plot(f, np.abs(fft_data))
  plt.xlabel('Frequency in Hertz [Hz]')
  plt.ylabel('Magnitude')
  plt.title('FFT')
  draw_plot(plot_save_path)
  plt.close()

  max_amp = 0
  max_index = 0
  index = 0
  for c in fft_data:
    if f[index] < f_low or f[index] > f_high:
      index = index + 1
      continue;
    real = np.real(c)
    img = np.imag(c)
    amp = np.sqrt(real*real + img*img)
    if max_amp < amp:
      max_amp = amp
      max_index = index
    index = index + 1

  return max_amp, f[max_index]

def calculate_breathing_rate(normalized_data):
  smooth_data = apply_average_filter(normalized_data, average_filter_window_duration_br)
  plot(smooth_data[:,0], 'Smoothened Accelerometer Data', 'plots/bio_watch/smoothened_ax.png')

  amp_to_freq = {}
  breathing_low_freq = 0.13
  breathing_high_freq = 0.66
  print('Max Amplitude within 0.13 and 0.66 Hz frequency:')
  br_x_amp, br_x_f = fft(smooth_data[:,0], breathing_low_freq, breathing_high_freq, 'plots/bio_watch/br_fft_xaxis.png')
  amp_to_freq[br_x_amp] = br_x_f
  print('X-Axis:', br_x_amp)
  br_y_amp, br_y_f = fft(smooth_data[:,1], breathing_low_freq, breathing_high_freq, 'plots/bio_watch/br_fft_yaxis.png')
  amp_to_freq[br_y_amp] = br_y_f
  print('Y-Axis:', br_y_amp)
  br_z_amp, br_z_f = fft(smooth_data[:,2], breathing_low_freq, breathing_high_freq, 'plots/bio_watch/br_fft_zaxis.png')
  amp_to_freq[br_z_amp] = br_z_f
  print('Z-Axis:', br_z_amp)
  br_max_amp = max([br_x_amp, br_y_amp, br_z_amp])

  print("Max amplitude chosen:", br_max_amp)
  print("Frequency of chosen amplitude:", amp_to_freq[br_max_amp])
  print("Respiratory Rate (bpm):", 60*amp_to_freq[br_max_amp])
  return 60*amp_to_freq[br_max_amp]

def calculate_heart_rate(normalized_data):
  smooth_data = apply_average_filter(normalized_data, average_filter_window_duration_hr)
  smooth_data = np.array(list(filter(lambda row: np.isfinite(np.sum(row)), smooth_data)), dtype=np.float64)
  plot(smooth_data[:,0], 'Smoothened Accelerometer Data - HR', 'plots/bio_watch/smoothened_ax_hr.png')

  low_cutoff_freq = 4
  high_cutoff_freq = 11
  smooth_data[:,0] = apply_bandpass_butterworth_filter(smooth_data[:,0], low_cutoff_freq, high_cutoff_freq)
  smooth_data[:,1] = apply_bandpass_butterworth_filter(smooth_data[:,1], low_cutoff_freq, high_cutoff_freq)
  smooth_data[:,2] = apply_bandpass_butterworth_filter(smooth_data[:,2], low_cutoff_freq, high_cutoff_freq)
  plot(smooth_data[:,0], 'Bandpass-1 Accelerometer Data', 'plots/bio_watch/bandpass1_ax.png')

  aggregated_data = aggregate_components(smooth_data)

  high_cutoff_freq = 2.5
  low_cutoff_freq = 0.66
  bandpass2_data = apply_bandpass_butterworth_filter(aggregated_data, low_cutoff_freq, high_cutoff_freq)
  plot(bandpass2_data, 'Pulse wave from Accelerometer Data', 'plots/bio_watch/pulse_wave.png')

  max_amp, max_freq = fft(bandpass2_data, 0.66, 2.5, 'plots/bio_watch/hr_fft.png')
  print('Max Amplitude:', max_amp)
  print('Max Frequency:', max_freq)
  print('Heart Rate (bpm):', 60*max_freq)
  return 60*max_freq

def bio_watch(data, sampling_freq):
  global sampling_frequency
  sampling_frequency = sampling_freq
  plot(data[:,0], 'Raw Accelerometer Data', 'plots/bio_watch/raw_ax.png')
  normalized_data = normalize(data)
  plot(normalized_data[:,0], 'Normalized Accelerometer Data', 'plots/bio_watch/normalized.png')

  hr = calculate_heart_rate(normalized_data)
  br = calculate_breathing_rate(normalized_data)
  return hr, br

if __name__ == '__main__':
  data = pd.read_csv(input_file_path).values
  print("Number of records:", len(data))

  bio_watch(data, sampling_frequency)

