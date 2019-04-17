import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import scipy.fftpack
import scipy as sp
from scipy.stats import zscore
import pandas as pd
from scipy.signal import butter, lfilter

input_file_path = "HMP_Dataset/Liedown_bed/Accelerometer-2011-06-02-17-21-57-liedown_bed-m1.txt"
sampling_frequency = 32
average_filter_window_duration = int((1/7)*sampling_frequency)
T = 1/sampling_frequency

def normalize(data):
	data[:,0] = sp.stats.zscore(data[:,0])
	data[:,1] = sp.stats.zscore(data[:,1])
	data[:,2] = sp.stats.zscore(data[:,2])
	return data

def apply_average_filter(data):
	data[:,0] = np.array(pd.Series(data[:,0]).rolling(window=average_filter_window_duration).mean())
	data[:,1] = np.array(pd.Series(data[:,1]).rolling(window=average_filter_window_duration).mean())
	data[:,2] = np.array(pd.Series(data[:,2]).rolling(window=average_filter_window_duration).mean())
	return data

def plot(data, title):
  x = data
  y = list(range(0, len(data)))
  plt.plot(y, x)

  plt.title(title)
  plt.ylabel('ACCELERATION Ax (m/s^2)')
  plt.xlabel('TIME (s)')
  plt.draw()
  plt.pause(5)
  plt.close()

def butter_bandpass(lowcut, highcut, fs, order):
  nyq = 0.5 * fs
  low = lowcut / nyq
  high = highcut / nyq
  b, a = butter(order, [low, high], btype='band')
  return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
  b, a = butter_bandpass(lowcut, highcut, fs, order)
  y = lfilter(b, a, data)
  return y

def apply_bandpass_butterworth_filter(data, low_cutoff_freq, high_cutoff_freq):
  order = 2
  data = butter_bandpass_filter(data, low_cutoff_freq, high_cutoff_freq, sampling_frequency, order)
  return data

def aggregate_components(data):
  data = np.array(list(map(lambda c: np.sqrt(np.sum(np.square(c))), data)))  
  return data

def fft(data):
  acc_data = data[:,0]
  acc_data = acc_data[~np.isnan(acc_data)]
  N = len(acc_data)
  T = 1/sampling_frequency
  t = np.linspace(0, N/sampling_frequency, N)
  plt.ylabel("Amplitude")
  plt.xlabel("Time [s]")
  plt.plot(t, acc_data)
  plt.draw()
  plt.pause(5)
  plt.close()

  fft_data = sp.fftpack.fft(acc_data)
  T = t[1] - t[0]
  f = np.linspace(0, 1/T, N)

  plt.plot(f[:N // 2], np.abs(fft_data)[:N // 2] * 1 / N)
  plt.xlabel('Frequency in Hertz [Hz]')
  plt.ylabel('Magnitude')
  plt.title('FFT')
  plt.draw()
  plt.pause(5)
  plt.close()

  max_amp = 0
  max_c = 0
  max_index = 0
  index = 0
  for c in fft_data:
    real = np.real(c)
    img = np.imag(c)
    amp = np.sqrt(real*real + img*img)
    if max_amp < amp:
      max_amp = amp
      max_c = c
      max_index = index
    index = index + 1

  print('Max Amplitude:', max_amp)
  print('Heart Rate:', (60*sampling_frequency)/(T*N))
  return

if __name__ == '__main__':
  data = np.loadtxt(input_file_path)
  plot(data[:,0], 'Raw Accelerometer Data')
  print("Number of records:", len(data))

  normalized_data = normalize(data)
  plot(normalized_data[:,0], 'Normalized Accelerometer Data')

  smooth_data = apply_average_filter(normalized_data)
  plot(smooth_data[:,0], 'Smoothened Accelerometer Data')

  high_cutoff_freq = 4
  low_cutoff_freq = 11
  bandpass1_data = apply_bandpass_butterworth_filter(smooth_data, low_cutoff_freq, high_cutoff_freq)
  plot(bandpass1_data[:,0], 'Bandpass-1 Accelerometer Data')

  # aggregated_data = aggregate_components(bandpass1_data)

  high_cutoff_freq = 2.5
  low_cutoff_freq = 0.66
  bandpass2_data = apply_bandpass_butterworth_filter(bandpass1_data, low_cutoff_freq, high_cutoff_freq)
  plot(bandpass2_data, 'Bandpass-2 Accelerometer Data')

  fft(bandpass2_data)

