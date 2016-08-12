import time
import alsaaudio
import numpy as np


class AudioInterface:
    """
    Manages the sound interface. This manages the main callback for the audio
    interface and delegates behaviour to the Playback and Recording modules.
    """

    def __init__(self,
                 playback_queue,
                 recording_queue,
                 n_channels,
                 sample_rate,
                 sample_width,
                 output_device_id,
                 input_device_id,
                 frame_count=1024):
        self.playback_queue = playback_queue
        self.recording_queue = recording_queue
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.frame_count = frame_count

        print("frame_count: {}".format(frame_count))

        print("available cards: {}".format(alsaaudio.cards()))
        print("available PCMs: {}".format(alsaaudio.pcms()))

        self.in_stream = alsaaudio.PCM(
            type=alsaaudio.PCM_CAPTURE,
            mode=alsaaudio.PCM_NONBLOCK,
            device=input_device_id)
        self.in_stream.setchannels(2)
        self.in_stream.setrate(self.sample_rate)
        self.in_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.in_stream.setperiodsize(self.frame_count)
        print("in_stream card: {}".format(self.in_stream.cardname()))

        self.out_stream = alsaaudio.PCM(
            type=alsaaudio.PCM_PLAYBACK,
            device=output_device_id)
        self.out_stream.setchannels(self.n_channels)
        self.out_stream.setrate(self.sample_rate)
        self.out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.out_stream.setperiodsize(self.frame_count)
        print("out_stream card: {}".format(self.out_stream.cardname()))


        print("Finished initialising audio")

        # Loopback stuff
        self.loopback_channels_left = [i for i in range(0, self.n_channels//2)]
        self.loopback_channels_right = [i for i in range(self.n_channels//2, self.n_channels)]


    def start_stream(self):
        pass


    def close_stream(self):
        pass


    def is_active(self):
        return True


    def loopback_audio(self):
        """
        Reads input from the loopback device, and then prepares it for output
        """
        loopback_buffer = self.in_stream.read()

        loopback_input = np.frombuffer(
            loopback_buffer, dtype=np.int16).reshape(-1, 2)


        # print("ch 0 max: {}, ch 1 max: {}".format(
        #     np.abs(loopback_input[:,0]).max(), np.abs(loopback_input[:,0]).max()))

        # Now map onto the correct output channels
        loopback_output = np.zeros(
            (loopback_input.shape[0], self.n_channels), dtype=np.int16)
        loopback_output[:,self.loopback_channels_left] = loopback_input[:,[0]]
        loopback_output[:,self.loopback_channels_right] = loopback_input[:,[1]]

        print("channels max: {}".format(np.abs(loopback_output).max(axis=0)))

        return loopback_output


    def process_audio_chunk(self):
        st = time.time()

        # Send recording data
        if self.recording_queue is not None:
            pass
            # in_data = self.in_stream.read()
            # if in_data[0]:
            #      self.recording_queue.put(in_data)

        loopback_samples = self.loopback_audio()
        # Get output audio
        samples = self.playback_queue.get()

        samples += loopback_samples

        te = time.time() - st
        # print("Time elapsed: {}".format(te))

        st = time.time()
        self.out_stream.write(samples)
        # print("Write time: {}".format(time.time() - st))


    def run(self):
        while True:
            self.process_audio_chunk()
