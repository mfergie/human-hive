import pyaudio
import wave
import time
import sys
import numpy as np


import mock
import sys
sys.modules.update((mod_name, mock.Mock()) for mod_name in ['matplotlib', 'matplotlib.pyplot', 'matplotlib.image'])

import librosa


p = pyaudio.PyAudio()

n_channels=2
device_index=2
sample_rate=48000
frames_per_buffer=1024 * 1

def callback(in_data, frame_count, time_info, status, last_theta=[0]):
    start_theta = last_theta[0]
    end_theta = start_theta + 440*(frame_count/41000.0) * 2*np.pi
    last_theta[0] = end_theta
    sin_data = np.sin(np.linspace(start_theta, end_theta, frame_count))
    # print(sin_data)
    data = np.zeros((frame_count, n_channels), dtype=np.float32)
    # print(data.shape)
    data[:,0] = np.floor(sin_data * (2**15))
    print(data)
 
    data *= 0.1

    npdata = np.asarray(data, dtype=np.int16)
    #npdata = librosa.util.buf_to_int(data, n_bytes=2)
    print("zero_elements: {}".format(np.count_nonzero(npdata[:,0] == 0)))

    #print(npdata)
    return (npdata, pyaudio.paContinue)

print("Device parameters: {}".format(p.get_default_output_device_info()))

def bound_callback(in_data, frame_count, time_info, status):
    return callback(in_data, frame_count, time_info, status)

stream = p.open(format=p.get_format_from_width(2),
                channels=n_channels,
                rate=sample_rate,
                output=True,
                output_device_index=device_index,
#                frames_per_buffer=frames_per_buffer,
#                stream_callback=callback
)

stream.start_stream()

while stream.is_active():
    (data, flags) = bound_callback(None, frames_per_buffer, None, None)
    stream.write(data, frames_per_buffer)
    #time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()
