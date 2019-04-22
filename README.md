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
