import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import scipy.fftpack
import scipy as sp
import pandas as pd
from scipy.stats import zscore
from scipy.signal import butter, lfilter
from scipy import signal

style.use('ggplot')
save_plots = False

# Source: https://archive.ics.uci.edu/ml/datasets/MHEALTH+Dataset
input_file_path = 'datasets/uic_dataset.csv'

sampling_frequency = 50
highpass_cutoff_frequency = 5.6
lowpass_cutoff_frequency = 0.66 #TODO: Validate lowpass cutoff frequency

hr_min_freq = 0.66 #TODO: Validate assumption of filtering freq in range
hr_max_freq = 2.5
br_min_freq = 0.13
br_max_freq = 0.66

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

def fft(data, f_low, f_high, plot_save_path):
  N = len(data)
  fft_data = sp.fftpack.fft(data)
  f = np.linspace(0, N/sampling_frequency, N)
  plt.plot(f[:N // 2], np.abs(fft_data)[:N // 2] * 1 / N)
  plt.xlabel('Frequency in Hertz [Hz]')
  plt.ylabel('Amplitude')
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

  print('Max Amplitude:', max_amp)
  print('Frequency:',f[max_index])
  return 60*f[max_index]

def butter_pass_filter(data, cutoff, fs, btype, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    y = lfilter(b, a, data)
    return y

def normalize(data):
  data[:,0] = sp.stats.zscore(data[:,0])
  data[:,1] = sp.stats.zscore(data[:,1])
  data[:,2] = sp.stats.zscore(data[:,2])
  return data

def apply_pass_filter(unfiltered_data, btype, cutoff, plot_save_path):
  t = np.linspace(0, len(unfiltered_data)/sampling_frequency, len(unfiltered_data), endpoint=False)
  filtered_data = np.full_like(unfiltered_data, 0)
  axes = {'x': 0, 'y': 1, 'z': 2}

  plt.figure(figsize=(12,8))
  for axis, index in axes.items():
    filtered_data[:,index] = butter_pass_filter(unfiltered_data[:,index], cutoff, sampling_frequency, btype, 2)

    plt.subplot(len(axes), 1, index+1)
    plt.plot(t, unfiltered_data[:,index], 'b-', label="data %s-axis" % axis)
    plt.plot(t, filtered_data[:,index], 'g-', linewidth=2, label="filtered data %s-axis" % axis)
    plt.xlabel('Time [sec]')
    plt.grid()
    plt.legend()
    plt.subplots_adjust(hspace=0.35)
  plt.title("%s pass filtering" % btype)
  draw_plot(plot_save_path)
  plt.close()
  return filtered_data

def seismotracker(data, sampling_freq):
  plot(data[:,0], 'Unfiltered Raw Accelerometer Data', 'plots/seismotracker/raw_ax.png')

  global sampling_frequency
  sampling_frequency = sampling_freq
  normalized_data = normalize(data)
  print('Breathing Rate:')

  print("X-Axis:")    
  breathing_rate_x = fft(normalized_data[:,0], br_min_freq, br_max_freq, 'plots/seismotracker/br_fft_xaxis.png')
  print("Respiration Rate (bpm):", breathing_rate_x)

  print("Y-Axis:")
  breathing_rate_y = fft(normalized_data[:,1], br_min_freq, br_max_freq, 'plots/seismotracker/br_fft_yaxis.png')
  print("Respiration Rate (bpm):", breathing_rate_y)

  print("Z-Axis:")    
  breathing_rate_z = fft(normalized_data[:,2], br_min_freq, br_max_freq, 'plots/seismotracker/br_fft_zaxis.png')
  print("Respiration Rate (bpm):", breathing_rate_z)
  avg_br = (breathing_rate_x + breathing_rate_y + breathing_rate_z)/3
  print("Average Respiration Rate (bpm):", avg_br)

  print('\nHeart Rate:')
  highpass_filtered_data = apply_pass_filter(normalized_data, 'high', highpass_cutoff_frequency, 'plots/seismotracker/hr_highpass_filtering.png')
  lowpass_filtered_data = apply_pass_filter(highpass_filtered_data, 'low', lowpass_cutoff_frequency, 'plots/seismotracker/hr_lowpass_filtering.png')

  # squared_signal = lowpass_filtered_data * lowpass_filtered_data # TODO: Squaring signal?

  print("X-Axis:")    
  heart_rate_x = fft(lowpass_filtered_data[:,0], hr_min_freq, hr_max_freq, 'plots/seismotracker/hr_fft_xaxis.png')
  print("Heart Rate (bpm):", heart_rate_x)

  print("Y-Axis:")    
  heart_rate_y = fft(lowpass_filtered_data[:,1], hr_min_freq, hr_max_freq, 'plots/seismotracker/hr_fft_xaxis.png')
  print("Heart Rate (bpm):", heart_rate_y)

  print("Z-Axis:")    
  heart_rate_z = fft(lowpass_filtered_data[:,2], hr_min_freq, hr_max_freq, 'plots/seismotracker/hr_fft_zaxis.png')
  print("Heart Rate (bpm):", heart_rate_z)
  avg_hr = (heart_rate_x + heart_rate_y + heart_rate_z)/3
  print("Average Heart Rate (bpm):", avg_hr)
  return avg_hr, avg_br

if __name__ == '__main__':
  data = pd.read_csv(input_file_path).values
  print("Number of records:", len(data))
  seismotracker(data, sampling_frequency)


