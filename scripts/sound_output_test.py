import pyaudio
import wave
import time
import sys
import numpy as np

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()

DEVICE_ID=2

def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    # npdata = np.frombuffer(data, dtype=np.int16)
    return (data, pyaudio.paContinue)

print("Device parameters: {}".format(p.get_default_output_device_info()))


stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output_device_index=DEVICE_ID,
                output=True,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()
wf.close()

p.terminate()
