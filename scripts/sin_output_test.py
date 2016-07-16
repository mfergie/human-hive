import pyaudio
import wave
import time
import sys
import numpy as np


p = pyaudio.PyAudio()

n_channels=6

def callback(in_data, frame_count, time_info, status, last_theta=[0]):
    start_theta = last_theta[0]
    end_theta = start_theta + 440*(frame_count/41000.0) * 2*np.pi
    last_theta[0] = end_theta
    sin_data = np.sin(np.linspace(start_theta, end_theta, frame_count))
    # print(sin_data)
    data = np.zeros((frame_count, n_channels), dtype=np.float32)
    # print(data.shape)
    data[:,5] = np.floor(sin_data * (2**15))
    print(data)

    data *= 0.1

    npdata = np.asarray(data, dtype=np.int16)

    #print(npdata)
    return (npdata, pyaudio.paContinue)

print("Device parameters: {}".format(p.get_default_output_device_info()))

def bound_callback(in_data, frame_count, time_info, status):
    return callback(in_data, frame_count, time_info, status)

stream = p.open(format=p.get_format_from_width(2),
                channels=n_channels,
                rate=41000,
                output=True,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()
