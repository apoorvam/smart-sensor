import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import scipy.fftpack
import scipy as sp
from scipy.stats import zscore
import pandas as pd

input_file_path = "HMP_Dataset/Liedown_bed/Accelerometer-2011-06-02-17-21-57-liedown_bed-m1.txt"
sampling_frequency = 32
average_filter_window_duration = (1/7)*sampling_frequency

def normalize(data):
	data[:,0] = sp.stats.zscore(data[:,0])
	data[:,1] = sp.stats.zscore(data[:,1])
	data[:,2] = sp.stats.zscore(data[:,2])
	return data

def apply_average_filter(data):
	data[:,0] = np.array(pd.Series(data[:,0]).rolling(window=4).mean())
	data[:,1] = np.array(pd.Series(data[:,1]).rolling(window=4).mean())
	data[:,2] = np.array(pd.Series(data[:,2]).rolling(window=4).mean())
	return data

def plot_ax(data):
  x = np.array(data[:,0])
  y = list(range(0, len(data)))
  plt.plot(y, x)

  plt.title('Accelerometer Data')
  plt.ylabel('ACCELERATION Ax (m/s^2)')
  plt.xlabel('TIME (s)')
  plt.draw()
  plt.pause(5)
  plt.close()


if __name__ == '__main__':
  data = np.loadtxt(input_file_path)
  plot_ax(data)
  print("Number of records:", len(data))
  normalized_data = normalize(data)
  plot_ax(normalized_data)
  smooth_data = apply_average_filter(normalized_data)
  plot_ax(smooth_data)
