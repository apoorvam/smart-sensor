import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import scipy.fftpack
import scipy as sp
from scipy.stats import zscore
from scipy.signal import butter, lfilter
from scipy import signal

style.use('ggplot')

input_file_path = "HMP_Dataset/Liedown_bed/Accelerometer-2011-06-02-17-21-57-liedown_bed-m1.txt"
sampling_frequency = 32
highpass_cutoff_frequency = 5.6
lowpass_cutoff_frequency = 0.66 #TODO: Validate lowpass cutoff frequency

def plot(data, title):
  N = len(data)
  y = np.linspace(0, sampling_frequency, N)
  plt.plot(y, data)

  plt.title(title)
  plt.ylabel('ACCELERATION Ax (m/s^2)')
  plt.xlabel('TIME (s)')
  plt.draw()
  plt.pause(5)
  plt.close()

def fft(data):
  N = len(data)

  fft_data = sp.fftpack.fft(data)
  f = np.linspace(0, sampling_frequency, N)

  plt.plot(f[:N // 2], np.abs(fft_data)[:N // 2] * 1 / N)
  plt.xlabel('Frequency in Hertz [Hz]')
  plt.ylabel('Amplitude')
  plt.title('FFT')
  plt.draw()
  plt.pause(5)
  plt.close()

  max_amp = 0
  max_index = 0
  index = 0
  for c in fft_data:
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

def apply_pass_filter(unfiltered_data, btype, cutoff):
  t = np.linspace(0, sampling_frequency, len(unfiltered_data), endpoint=False)
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
  plt.draw()
  plt.pause(10)
  plt.close()
  return filtered_data

if __name__ == '__main__':
  data = np.loadtxt(input_file_path)
  plot(data[:,0], 'Unfiltered Raw Accelerometer Data')
  print("Number of records:", len(data))

  normalized_data = normalize(data)
  print('Breathing Rate\n--------------')

  print("X-Axis:")    
  breathing_rate = fft(normalized_data[:,0])
  print("Respiration Rate (bpm):", breathing_rate)

  print("Y-Axis:")
  breathing_rate = fft(normalized_data[:,1])
  print("Respiration Rate (bpm):", breathing_rate)

  print("Z-Axis:")    
  breathing_rate = fft(normalized_data[:,2])
  print("Respiration Rate (bpm):", breathing_rate)

  print('\nHeart Rate\n----------')
  highpass_filtered_data = apply_pass_filter(normalized_data, 'high', highpass_cutoff_frequency)
  lowpass_filtered_data = apply_pass_filter(highpass_filtered_data, 'low', lowpass_cutoff_frequency)

  # squared_signal = lowpass_filtered_data * lowpass_filtered_data # TODO: Squaring signal?

  print("X-Axis:")    
  heart_rate = fft(lowpass_filtered_data[:,0])
  print("Heart Rate (bpm):", heart_rate)

  print("Y-Axis:")    
  heart_rate = fft(lowpass_filtered_data[:,1])
  print("Heart Rate (bpm):", heart_rate)

  print("Z-Axis:")    
  heart_rate = fft(lowpass_filtered_data[:,2])
  print("Heart Rate (bpm):", heart_rate)



