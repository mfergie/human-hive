import sounddevice as sd
import time
import numpy as np
from humanhive import loopback

class AudioInterface:
    """
    Manages the sound interface. This manages the main callback for the audio
    interface and delegates behaviour to the Playback and Recording modules.
    """

    def __init__(self,
                 playback_queue,
                 recording_queue,
                 loopback_queue,
                 n_channels,
                 sample_rate,
                 sample_width,
                 output_device_id,
                 input_device_id,
                 frame_count=1024,
                 mpctx=None):
        self.playback_queue = playback_queue
        self.recording_queue = recording_queue
        self.loopback_queue = loopback_queue
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.frame_count = frame_count

        print("frame_count: {}".format(frame_count))

        print("Sound devices:")
        print(sd.query_devices())

        self.loopback_channels_left = [
            i for i in range(0, self.n_channels//2)]
        self.loopback_channels_right = [
            i for i in range(self.n_channels//2, self.n_channels)]

        self.channel_volumes = None


        output_device_id = int(output_device_id)
        input_device_id = int(input_device_id)

        self.stream = sd.Stream(
            samplerate=self.sample_rate,
            blocksize=self.frame_count,
            device=(input_device_id, output_device_id),
            channels=(2, self.n_channels),
            dtype=np.int16,
            callback=self.callback)

        self.loopback_volume_threshold = 20

    def start_stream(self):
        self.stream.start()


    def close_stream(self):
        self.stream.stop()
        self.stream.close()


    def is_active(self):
        return self.stream.active


    def callback(self, indata, outdata, frames, time, status):
        """
        Audio processing callback.
        """

        indata_volume = np.abs(indata).mean()
        if indata_volume > self.loopback_volume_threshold:
            outdata[:] = loopback.loopback_channels(
                indata, self.loopback_channels_left, self.loopback_channels_right)
        else:
            outdata[:] = self.playback_queue.get(block=True)

        self.channel_volumes = np.abs(outdata).mean(axis=0)
        return None


    def run(self):
        self.start_stream()

        while self.is_active():
            print(self.stream.cpu_load)
            print("Channel volumes: {}".format(self.channel_volumes))
            time.sleep(0.1)
