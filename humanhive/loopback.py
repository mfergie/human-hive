"""
Contains Loopback, a class for taking stereo input in and outputting it over
n_channels.
"""
import numpy as np

class Loopback:

    def __init__(self,
                 audio_in,
                 audio_out,
                 n_channels_in,
                 n_channels_out):
        self.audio_in = audio_in
        self.audio_out = audio_out
        self.n_channels_in = n_channels_in
        self.n_channels_out = n_channels_out

        if self.n_channels_in != 2:
            raise ValueError("Only supports 2 input channels")

        self.loopback_channels_left = [
            i for i in range(0, self.n_channels_out//2)]
        self.loopback_channels_right = [
            i for i in range(self.n_channels_out//2, self.n_channels_out)]


    def process_audio(self):
        data_in = np.frombuffer(self.audio_in.get(), dtype=np.int16)
        loopback_input = data_in.reshape(-1, self.n_channels_in)

        # Now map onto the correct output channels
        loopback_output = np.zeros(
            (loopback_input.shape[0], self.n_channels_out), dtype=np.int16)
        loopback_output[:,self.loopback_channels_left] = loopback_input[:,[0]]
        loopback_output[:,self.loopback_channels_right] = loopback_input[:,[1]]

        print("loopback channels max: {}".format(np.abs(loopback_output).max(axis=0)))

        self.audio_out.put(loopback_output)


    def run(self):
        while True:
            self.process_audio()
