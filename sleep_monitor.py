import numpy as np

input_file_path = "HMP_Dataset/Liedown_bed/Accelerometer-2011-03-29-09-19-22-liedown_bed-f1.txt"
sampling_frequency = 32
segment_window_size = 1
acceleration_threshold = 10
motionless_sleep_threshold_in_window_percentage = 50

def get_input_data():
  data = np.loadtxt(input_file_path)
  size = len(data)
  
  # CONVERT THE ACCELEROMETER DATA INTO REAL ACCELERATION VALUES
  # mapping from [0. .63] to[-14.709.. + 14.709]
  # real_val = -1.5 g + (coded_val / 63) * 3 g
  real_data = list(map(lambda v: -14.709 + (v / 63) * (2 * 14.709), data))

  segmented_data = np.array_split(real_data, size / (segment_window_size * sampling_frequency))
  print("Number of segments:", len(segmented_data))
  print("Size of each segment:", len(segmented_data[0]))

  filtered_data = list(filter(lambda segment: is_valid_segment(segment), segmented_data))
  print("Number of filtered segments:", len(filtered_data))


def is_valid_segment(segment):
  window_size = len(segment)
  motionless_limit = window_size - (motionless_sleep_threshold_in_window_percentage/100)*window_size
  return len(list(filter(lambda tuple: np.linalg.norm([tuple[0], tuple[1], tuple[2]]) < acceleration_threshold, segment))) >= motionless_limit

if __name__ == "__main__":
  get_input_data()