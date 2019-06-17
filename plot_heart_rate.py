import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

input_file_path = 'datasets/uic_hr_dataset_lead2.csv'
sampling_frequency = 50

def plot_hr_graph(data):
  data = np.array(data)
  N = len(data)
  y = np.linspace(0, N/sampling_frequency, N)
  plt.plot(y, data)

  plt.title('Electrocardiogram signal')
  plt.ylabel('ECG amplitude')
  plt.xlabel('TIME (s)')
  plt.show()
  plt.pause(20)
  plt.close()
  return

if __name__ == '__main__':
  data = pd.read_csv(input_file_path).values
  print("Number of records:", len(data))
  plot_hr_graph(data)
