import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import scipy.fftpack
import scipy as sp

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

def plot_ax(data):
  x = np.array(data[:,0])
  y = list(range(0, len(data)))
  plt.plot(y, x)

  plt.title('Raw Accelerometer Data')
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

# Fast fourier transform
def apply_fft(data):
  print('Converting time domain signal to frequency domain...')
  x = data[:,0]

  X = sp.fftpack.fft(x)
  freqs = sp.fftpack.fftfreq(len(x)) * sampling_frequency
  # positive_freqs = np.array(list(map(lambda f: 0 if f < 0 or f > 0.5 else f, freqs)))

  fig, ax = plt.subplots()
  ax.stem(freqs, np.abs(X))

  ax.set_xlabel('Frequency in Hertz [Hz]')
  ax.set_ylabel('Magnitude')
  ax.set_title('FFT of the filtered data')
  ax.set_xlim(-0.25, 1)
  print(max(abs(X)))
  print(max(abs(freqs)))
  plt.show()
  return

if __name__ == '__main__':
  data = np.loadtxt(input_file_path)
  print("Number of records:", len(data))

  plot_ax(data)
  data = segment(data)
  data = preprocess(data)
  plot_ax(data)
  apply_fft(data)
