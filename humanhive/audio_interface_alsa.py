import time
import alsaaudio


class AudioInterface:
    """
    Manages the sound interface. This manages the main callback for the audio
    interface and delegates behaviour to the Playback and Recording modules.
    """

    def __init__(self,
                 playback,
                 recording_queue,
                 n_channels,
                 sample_rate,
                 sample_width,
                 device_id,
                 frame_count=1024):
        self.playback = playback
        self.recording_queue = recording_queue
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.frame_count = frame_count

        print("frame_count: {}".format(frame_count))

        self.in_stream = alsaaudio.PCM(
            cardindex=device_id)
        self.in_stream.setchannels(self.n_channels)
        self.in_stream.setrate(self.sample_rate)
        self.in_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.in_stream.setperiodsize(self.frame_count)


        print("Finished initialising audio")


    def audio_callback(self, in_data, frame_count, time_info, status):
        st = time.time()
        # Send recording data
        if self.recording_queue is not None:
            self.recording_queue.put((in_data, frame_count))

        # Get output audio
        samples = self.playback.get()

        te = time.time() - st
        print("Time elapsed: {}".format(te))

        return (samples, pyaudio.paContinue)


    def start_stream(self):
        pass


    def close_stream(self):
        pass


    def is_active(self):
        return True

    def run(self):
        while True:
            (data, status) = self.audio_callback(
                None, self.frame_count, None, None)
            st = time.time()
            self.in_stream.write(data)
            print("Write time: {}".format(time.time() - st))
