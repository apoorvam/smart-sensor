import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import scipy.fftpack
import scipy as sp
from scipy import signal
import math
import warnings
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

input_file_path = "HMP_Dataset/Liedown_bed/Accelerometer-2011-06-02-17-21-57-liedown_bed-m1.txt"
sampling_frequency = 32
segment_window_size = 1
acceleration_threshold = 10
motionless_sleep_threshold_in_window_percentage = 50
tv_filter_lambda = 5

style.use('ggplot')

def segment(data):
  size = len(data)
  print('Segmenting data...')
  
  # CONVERT THE ACCELEROMETER DATA INTO REAL ACCELERATION VALUES
  # mapping from [0. .63] to[-14.709.. + 14.709]
  # real_val = -1.5 g + (coded_val / 63) * 3 g
  real_data = list(map(lambda v: -14.709 + (v / 63) * (2 * 14.709), data))

  segmented_data = np.array_split(real_data, size / (segment_window_size * sampling_frequency))
  print("Number of segments:", len(segmented_data))
  print("Size of each segment:", len(segmented_data[0]))

  print('Removing segments with motion...')
  filtered_data = np.array(list(filter(lambda segment: is_valid_segment(segment), segmented_data)))
  print("Number of filtered segments:", len(filtered_data))
  flattened_data = np.array([e for sl in filtered_data for e in sl])
  print("Number of records:", len(flattened_data))
  return flattened_data

def is_valid_segment(segment):
  window_size = len(segment)
  motionless_limit = window_size - (motionless_sleep_threshold_in_window_percentage/100)*window_size
  return len(list(filter(lambda tuple: np.linalg.norm([tuple[0], tuple[1], tuple[2]]) < acceleration_threshold, segment))) >= motionless_limit

def plot_ax(data, title):
  x = np.array(data[:,0])
  N = len(x)
  y = np.linspace(0, sampling_frequency, N)
  plt.plot(y, x)

  plt.title(title)
  plt.ylabel('ACCELERATION Ax (m/s^2)')
  plt.xlabel('TIME (s)')
  plt.draw()
  plt.pause(5)
  plt.close()

def preprocess(data):
  print('Denoisifying data...')
  data[:,0] = denoisify(data[:,0], tv_filter_lambda, len(data))
  data[:,1] = denoisify(data[:,1], tv_filter_lambda, len(data))
  data[:,2] = denoisify(data[:,2], tv_filter_lambda, len(data))
  return data

def clip(x, b):
  return np.where(x <= b, x, b * np.sign(x))

# Total variation filter
def denoisify(y, lambda_value, nit):
  J = np.zeros((1, nit))
  N = len(y)
  z = np.zeros((1, N-1))
  alpha = 4
  T = lambda_value / 2
  for k in range(0, N-1):
    x = y - np.c_[-z[0][0], -np.diff(z, n=1), z[len(z)-1][len(z)-1]]
    abs = np.abs(x-y)
    J[0][k] = np.sum(abs*abs) + lambda_value * np.sum(np.abs(np.diff(x)))
    z = z + (1/alpha) * np.diff(x)
    z = np.vectorize(clip)(z, T)
  return x

def apply_kalman_filter(data):
  print("Performing multi-axis fusion by Kalman filter...")
  segment_size_for_kalman = 4 * sampling_frequency
  n_segments = math.ceil(len(data)/segment_size_for_kalman) +1
  rhat = np.zeros(n_segments)    # a posteri estimate of rr
  rhatminus = np.zeros(n_segments) # a priori estimate of rr
  p = np.zeros(n_segments)  # a posteri error estimate
  pminus = np.zeros(n_segments)  # a priori error estimate
  k = np.zeros(n_segments) # kalman gain

  r_measurement = np.zeros((n_segments, 3)) # observation measurements

  # initial guesses
  p[0] = 1.0  
  rhat[0] = 40
  for segment_number in range(1, n_segments):
    segment = get_segment(data, segment_number-1, segment_size_for_kalman)
    f_x, fft_data_x, max_amp_x, max_index_x = fft(segment[:,0])
    f_y, fft_data_y, max_amp_y, max_index_y = fft(segment[:,1])
    f_z, fft_data_z, max_amp_z, max_index_z = fft(segment[:,2])
    r_measurement[segment_number] = [f_x[max_index_x] * 60, f_y[max_index_y] * 60, f_z[max_index_z] * 60]  
    variance_x = np.var(r_measurement[:,0])
    variance_y = np.var(r_measurement[:,1])
    variance_z = np.var(r_measurement[:,2])
    total_variance = variance_x + variance_y + variance_z

    # time update
    rhatminus[segment_number] = rhat[segment_number-1]
    pminus[segment_number] = p[segment_number-1]

    # measurement update
    n_f = [variance_x/total_variance, variance_y/total_variance, variance_z/total_variance]
    z = (n_f[0] * r_measurement[segment_number][0]) + (n_f[1] * r_measurement[segment_number][1]) + (n_f[2] * r_measurement[segment_number][2])
    r = np.sqrt(np.sum(list(map(lambda index: np.square(n_f[index] * (r_measurement[segment_number][index] - z)), [0, 1, 2])))) # variance of the measurement noise
    if (pminus[segment_number]!=0 or r != 0):
      k[segment_number] = pminus[segment_number] /(pminus[segment_number] + r)

    rhat[segment_number] = rhatminus[segment_number] + k[segment_number] * (z - rhatminus[segment_number]) 
    p[segment_number] = (1 - k[segment_number]) * pminus[segment_number]

  print("Breathing rate from Kalman filter:", rhat[n_segments-1])

def get_segment(data, segment_number, segment_size):
  return data[segment_number*segment_size: segment_number*segment_size+segment_size]

def apply_fft_on_xyz(data):
  print('X-Axis')
  r_x = apply_fft(data[:,0], 'FFT of the filtered data X-Axis')
  print('Y-Axis')
  r_y = apply_fft(data[:,1], 'FFT of the filtered data Y-Axis')
  print('Z-Axis')
  r_z = apply_fft(data[:,2], 'FFT of the filtered data Z-Axis')
  print('Average Respiratory rate (bpm):', (r_x+r_y+r_z)/3)
  return r_x, r_y, r_z

def fft(data):
  N = len(data)
  data = sp.signal.detrend(data)
  fft_data = sp.fftpack.fft(data)
  f = np.linspace(0, sampling_frequency, N)

  max_amp = 0
  max_index = 0
  index = 0
  for c in fft_data[:N//2]:
    real = np.real(c)
    img = np.imag(c)
    amp = np.sqrt(real*real + img*img)
    if max_amp < amp:
      max_amp = amp
      max_index = index
    index = index+1
  return f, fft_data, max_amp, max_index

# Fast fourier transform
def apply_fft(acc_data, title):
  N = len(acc_data)
  f, fft_data, max_amp, max_index = fft(acc_data)

  print('Max Amplitude:', max_amp)
  print('Respiratory rate:',f[max_index])
  print('Respiratory rate (bpm):',f[max_index]*60)

  plt.plot(f[:N // 2], np.abs(fft_data)[:N // 2] * 1 / N)
  plt.xlabel('Frequency in Hertz [Hz]')
  plt.ylabel('Magnitude')
  plt.title(title)
  plt.draw()
  plt.pause(5)
  plt.close()
  return f[max_index]*60

if __name__ == '__main__':
  data = np.loadtxt(input_file_path)
  print("Number of records:", len(data))
  plot_ax(data, 'Raw Accelerometer Data')

  data = segment(data)
  data = preprocess(data)
  plot_ax(data, 'Processed Accelerometer Data')

  print('Converting time domain signal to frequency domain by FFT...')
  # r_x, r_y, r_z = apply_fft_on_xyz(data)
  apply_kalman_filter(data)
