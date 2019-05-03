import pandas as pd
import numpy as np

input_file_path = "datasets/Accelerometer-2011-06-02-17-21-57-liedown_bed-m1.txt"
fields = ['15', '16', '17']

if __name__ == '__main__':
	# data = pd.read_csv(input_file_path, skipinitialspace=True, usecols=fields, delim_whitespace=True)
	# data.to_csv('uic_dataset.csv', index=False)

  # CONVERT THE ACCELEROMETER DATA INTO REAL ACCELERATION VALUES
  # mapping from [0. .63] to[-14.709.. + 14.709]
  # real_val = -1.5 g + (coded_val / 63) * 3 g
  data = np.loadtxt("datasets/Accelerometer-2011-05-30-10-38-41-liedown_bed-m1.txt")
  real_data = list(map(lambda v: -14.709 + (v / 63) * (2 * 14.709), data))
  np.savetxt("datasets/hmp_dataset1.csv", real_data, delimiter=",")
