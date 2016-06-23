import sys
import time
import math
import numpy as np
import pyaudio
from humanhive import samplestream

# Load file as mono
audio_data = samplestream.load_wave_file(sys.argv[1])[:,0]

ss = samplestream.SampleStream(audio_data)

# Initialise PyAudio
p = pyaudio.PyAudio()

start_theta = [0]

def callback(in_data, frame_count, time_info, status):
    # data = wf.readframes(frame_count)
    # npdata = np.frombuffer(data, dtype=np.int16)
    mono_data = ss.retrieve_samples(frame_count)

    end_theta = start_theta[0] + ((frame_count / (44100*20)) * 2*math.pi)
    theta = np.linspace(start_theta[0], end_theta, frame_count)
    start_theta[0] = end_theta
    left_vol = np.cos(theta)
    right_vol = np.sin(theta)

    stereo_data = np.asfarray(samplestream.copy_n_channels(mono_data, 2))

    stereo_data[:,0] *= left_vol
    stereo_data[:,1] *= right_vol

    stereo_data = np.asarray(stereo_data, dtype=np.int16)
    return (stereo_data, pyaudio.paContinue)


stream = p.open(format=p.get_format_from_width(2),
                channels=2,
                rate=44100,
                output=True,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()
wf.close()

p.terminate()
