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
  N = len(acc_data)
  T = 1/sampling_frequency

  yr = sp.fftpack.fft(acc_data)
  freqs = sp.fftpack.fftfreq(N)

  plt.bar(freqs, np.abs(yr)) 
  plt.xlabel('Frequency in Hertz [Hz]')
  plt.ylabel('Magnitude')
  plt.title('FFT')
  plt.show()

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
  print(bandpass1_data)

  # aggregated_data = aggregate_components(bandpass1_data)

  high_cutoff_freq = 2.5
  low_cutoff_freq = 0.66
  bandpass2_data = apply_bandpass_butterworth_filter(bandpass1_data, low_cutoff_freq, high_cutoff_freq)
  plot(bandpass2_data, 'Bandpass-2 Accelerometer Data')
  print(bandpass2_data)

  fft(bandpass2_data)

