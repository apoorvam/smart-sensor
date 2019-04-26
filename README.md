# Smart-Sensing

Analysis of various HR/BR estimation algorithms from accelerometer data. The goal is to extract/summarize the resting-state respiration rate and/or heart rate from wrist-accelerometer data. 

Dataset used: https://archive.ics.uci.edu/ml/datasets/Dataset+for+ADL+Recognition+with+Wrist-worn+Accelerometer

1. [Sleep Monitor](http://mcn.cse.psu.edu/paper/xiaosun/ubicomp-xiao17.pdf)
2. [Bio Watch](https://ieeexplore.ieee.org/abstract/document/7349394)
2. [SeismoTracker](https://dl.acm.org/citation.cfm?id=2892279)

## Sleep Monitor

### System Overview for Respiratory rate

1. Raw Accelerometer Data

![Raw Accelerometer Data](plots/sleep_monitor/raw_ax.png)

2. Segmentation

3. Processing - Total Variation filter

![Processed data](plots/sleep_monitor/processed_data.png)

4. FFT - Respiratory rate estimation on each axis

![FFT X-Axis](plots/sleep_monitor/fft_xaxis.png)
![FFT Y-Axis](plots/sleep_monitor/fft_yaxis.png)
![FFT Z-Axis](plots/sleep_monitor/fft_zaxis.png)

5. Multi axis fusion - Kalman filter

### Output

```sh
$ python3 sleep_monitor.py
Number of records: 736
Segmenting data...
Number of segments: 23
Size of each segment: 32
Removing segments with motion...
Number of filtered segments: 10
Number of records: 320
Denoisifying data...
Converting time domain signal to frequency domain by FFT...
Performing multi-axis fusion by Kalman filter...
Breathing rate from Kalman filter: 15.1181102362
```

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
![FFT](plots/bio_watch/fft.png)

4. Estimation of Respiratory wave and respiration rate

* Apply averaging filter
* Apply FFT to obtain Respiratory rate in frequency domain on each component and choose one component with most periodic signal. The  periodicity  level  was  defined as the maximum amplitude observed within 0.13 and 0.66 Hz in the frequency domain (corresponding  to 8 and 40 breaths per minute, respectively). 

![FFT](plots/bio_watch/fft_zaxis.png)

### Output

```sh
$ python3 bio_watch.py
Number of records: 736
Max Amplitude: 164.356553437
Max Frequency: 0.743169398907
Heart Rate (bpm): 44.5901639344
Max Amplitude within 0.13 and 0.66 Hz frequency:
X-Axis: 83.7839707083
Y-Axis: 134.28961208
Z-Axis: 193.645331484
Max amplitude chosen: 193.645331484
Frequency of chosen amplitude: 0.179523141655
Respiratory Rate (bpm): 10.7713884993
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
Number of records: 736
Breathing Rate
--------------
X-Axis:
Max Amplitude: 433.453768883
Frequency: 0.043537414966
Respiration Rate (bpm): 2.61224489796
Y-Axis:
Max Amplitude: 349.206476224
Frequency: 0.043537414966
Respiration Rate (bpm): 2.61224489796
Z-Axis:
Max Amplitude: 263.877034229
Frequency: 0.087074829932
Respiration Rate (bpm): 5.22448979592

Heart Rate
----------
X-Axis:
Max Amplitude: 0.445972110173
Frequency: 0.87074829932
Heart Rate (bpm): 52.2448979592
Y-Axis:
Max Amplitude: 0.549721723143
Frequency: 1.00136054422
Heart Rate (bpm): 60.0816326531
Z-Axis:
Max Amplitude: 0.930872303024
Frequency: 0.783673469388
Heart Rate (bpm): 47.0204081633

```