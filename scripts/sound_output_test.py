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

n_bytes_to_test = 1024 * 2 * 6

DEVICE_ID=2

def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    # npdata = np.frombuffer(data, dtype=np.int16)
    # print("len(data): {}, frame_count: {}".format(len(data), frame_count))
    if len(data) < n_bytes_to_test:
        wf.rewind()
        data = wf.readframes(frame_count)
	print("Rewinding")
    return (data, pyaudio.paContinue)

print("Device parameters: {}".format(p.get_device_info_by_index(DEVICE_ID)))


stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=48000,
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
