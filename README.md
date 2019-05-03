# Smart-Sensing

Analysis of various HR/BR estimation algorithms from accelerometer data. The goal is to extract/summarize the resting-state respiration rate and/or heart rate from wrist-accelerometer data. 

#### Datasets
* [UCI Mhealth Dataset](https://archive.ics.uci.edu/ml/datasets/MHEALTH+Dataset) - Dataset 1 - Wrist Accelerometer data of 62 seconds at 50Hz sampling frequency
* [Dataset for ADL Recognition with Wrist-worn Accelerometer Data Set](https://archive.ics.uci.edu/ml/datasets/Dataset+for+ADL+Recognition+with+Wrist-worn+Accelerometer) - Dataset 2 and 3 - Accelerometer data of 22 and 21 seconds resepctively of 32Hz sampling frequency

#### Publications
* [Bio Watch](https://ieeexplore.ieee.org/abstract/document/7349394)
* [Sleep Monitor](http://mcn.cse.psu.edu/paper/xiaosun/ubicomp-xiao17.pdf)
* [SeismoTracker](https://dl.acm.org/citation.cfm?id=2892279)

#### Results

Dataset 1: (datasets/uic_dataset.csv)

|               | Heart Rate(bpm) | Breathing Rate(bpm) |
|---------------|-----------------|---------------------|
| Bio Watch     | 103.233670      | 21.607122           |
| SeismoTracker | 106.834777      | 12.804168           |
| Sleep Monitor | -               | 8.442211            |

Dataset 2: (datasets/hmp_dataset1.csv)

|               | Heart Rate(bpm) | Breathing Rate(bpm) |
|---------------|-----------------|---------------------|
| Bio Watch     | 76.980598       | 11.266164           |
| SeismoTracker | 51.319823       | 18.775545           |
| Sleep Monitor | -               | 9.448819            |

Dataset 3: (datasets/hmp_dataset2.csv)

|               | Heart Rate(bpm) | Breathing Rate(bpm) |
|---------------|-----------------|---------------------|
| Bio Watch     | 88.256334       | 9.389671            |
| SeismoTracker | 73.858936       | 11.892541           |
| Sleep Monitor | -               | 9.448819            |

## Bio Watch

Estimation of heart and breathing rates from wrist motions, based on Ballistocardiography.

### System Overview for Heart Rate and Respiratory Rate

1. Accelerometer Data

![Raw Accelerometer Data](plots/bio_watch/raw_ax.png)

2. Normalization with z-score

X, Y, Z axes of accelerometer values are normalized with z-scores to give them same relevance. 

![Normalized data](plots/bio_watch/normalized.png)

3. Estimation of Pulse wave and pulse rate

* Averaging filter for each component to smoothen data
![Smoothened data](plots/bio_watch/smoothened_ax.png)

* Band pass butterworth filter of order 2 (4 Hz - 11 Hz)
![Bandpass 1 data](plots/bio_watch/bandpass1_ax.png)

* Aggregate components
* Band pass butterworth filter of order 2 (0.66 Hz - 2.5 Hz)
![Bandpass 2 data](plots/bio_watch/bandpass2_ax.png)

* Apply FFT to obtain Heart rate in frequency domain
![FFT](plots/bio_watch/hr_fft.png)

4. Estimation of Respiratory wave and respiration rate

* Apply averaging filter
* Apply FFT to obtain Respiratory rate in frequency domain on each component and choose one component with most periodic signal. The  periodicity  level  was  defined as the maximum amplitude observed within 0.13 and 0.66 Hz in the frequency domain (corresponding  to 8 and 40 breaths per minute, respectively). 

![FFT](plots/bio_watch/br_fft_xaxis.png)

### Output

```sh
$ python3 bio_watch.py
Max Amplitude: 22.077653592365234
Max Frequency: 1.7205611745513867
Heart Rate (bpm): 103.23367047308321
Max Amplitude within 0.13 and 0.66 Hz frequency:
X-Axis: 166.01035262050667
Y-Axis: 120.777797237787
Z-Axis: 115.25675615869969
Max amplitude chosen: 166.01035262050667
Frequency of chosen amplitude: 0.3601186943620178
Respiratory Rate (bpm): 21.60712166172107
```

## Sleep Monitor

### System Overview for Respiratory rate

1. Raw Accelerometer Data

![Raw Accelerometer Data](plots/sleep_monitor/raw_ax.png)

2. Segmentation

3. Processing - Total Variation filter

![Processed data](plots/sleep_monitor/processed_data.png)

4. FFT - Respiratory rate estimation on each axis

5. Multi axis fusion - Kalman filter

### Output

```sh
$ python3 sleep_monitor.py
Segmenting data...
Number of segments: 2
Size of each segment: 1536
Removing segments with motion...
Number of filtered segments: 2
Number of records: 3072
Denoisifying data...
Converting time domain signal to frequency domain by FFT...
X-Axis
Max Amplitude: 19.409012679761673
Respiratory rate: 0.1400455877564311
Respiratory rate (bpm): 8.402735265385866
Y-Axis
Max Amplitude: 11.459828693993831
Respiratory rate: 0.1400455877564311
Respiratory rate (bpm): 8.402735265385866
Z-Axis
Max Amplitude: 15.715620986587833
Respiratory rate: 0.1400455877564311
Respiratory rate (bpm): 8.402735265385866
Average Respiratory rate (bpm): 8.402735265385866
Performing multi-axis fusion by Kalman filter...
Breathing rate from Kalman filter: 8.442211055276381
```

## Seismotracker

Based on Seismocardiography(SCG) approach.

### System Overview for Heart Rate and Respiratory Rate

1. Raw Accelerometer Data

![Raw Accelerometer Data](plots/seismotracker/raw_ax.png)

2. Preprocessing - Normalize

3. Respiratory Rate estimation
- based on prevalent signal amplitude in frequency domain

X-Axis:

![Breathing Rate estimation - X Axis](plots/seismotracker/br_fft_xaxis.png)

Y-Axis:

![Breathing Rate estimation - Y Axis](plots/seismotracker/br_fft_yaxis.png)

Z-Axis:

![Breathing Rate estimation - Z Axis](plots/seismotracker/br_fft_zaxis.png)

4. High pass filter

![High pass filtering](plots/seismotracker/hr_highpass_filtering.png)


5. Low pass filter

![Low pass filtering](plots/seismotracker/hr_lowpass_filtering.png)

6. Heart Rate Estimation - FFT

X-Axis:

![Heart Rate estimation - X Axis](plots/seismotracker/hr_fft_xaxis.png)

Y-Axis:

![Heart Rate estimation - Y Axis](plots/seismotracker/hr_fft_yaxis.png)

Z-Axis:

![Heart Rate estimation - Z Axis](plots/seismotracker/hr_fft_zaxis.png)

### Output

```zsh
$ python3 seismotracker.py
Breathing Rate:
X-Axis:
Max Amplitude: 206.3525109611608
Frequency: 0.3601172256593943
Respiration Rate (bpm): 21.60703353956366
Y-Axis:
Max Amplitude: 181.17474579186927
Frequency: 0.1400455877564311
Respiration Rate (bpm): 8.402735265385866
Z-Axis:
Max Amplitude: 206.0686156672978
Frequency: 0.1400455877564311
Respiration Rate (bpm): 8.402735265385866
Average Respiration Rate (bpm): 12.80416802344513

Heart Rate:
X-Axis:
Max Amplitude: 1.335674895504559
Frequency: 1.7405665906870724
Heart Rate (bpm): 104.43399544122434
Y-Axis:
Max Amplitude: 1.4995635787466068
Frequency: 2.480807554542494
Heart Rate (bpm): 148.84845327254965
Z-Axis:
Max Amplitude: 1.497093668079774
Frequency: 1.120364702051449
Heart Rate (bpm): 67.22188212308693
Average Heart Rate (bpm): 106.8347769456203

```