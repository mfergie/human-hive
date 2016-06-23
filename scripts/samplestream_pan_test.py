import sys
import time
import numpy as np
import pyaudio
from humanhive import samplestream

# Load file as mono
audio_data = samplestream.load_wave_file(sys.argv[1])[:,0]

ss = samplestream.SampleStream(audio_data)

# Initialise PyAudio
p = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
    # data = wf.readframes(frame_count)
    # npdata = np.frombuffer(data, dtype=np.int16)
    mono_data = ss.retrieve_samples(frame_count)
    stereo_data = np.hstack(
        (mono_data[:, np.newaxis], mono_data[:, np.newaxis]))
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
