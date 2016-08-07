import time
import alsaaudio


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

        self.in_stream = alsaaudio.PCM(
            cardindex=output_device_id)
        self.in_stream.setchannels(self.n_channels)
        self.in_stream.setrate(self.sample_rate)
        self.in_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.in_stream.setperiodsize(self.frame_count)

        self.out_stream = alsaaudio.PCM(
            mode=alsaaudio.PCM_CAPTURE,
            cardindex=input_device_id)
        self.out_stream.setchannels(1)
        self.out_stream.setrate(self.sample_rate)
        self.out_stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.out_stream.setperiodsize(self.frame_count)


        print("Finished initialising audio")


    def start_stream(self):
        pass


    def close_stream(self):
        pass


    def is_active(self):
        return True

    def run(self):
        while True:
            st = time.time()

            # Send recording data
            if self.recording_queue is not None:
                in_data = self.out_stream.read()
                self.recording_queue.put(in_data)

            # Get output audio
            samples = self.playback_queue.get()

            te = time.time() - st
            # print("Time elapsed: {}".format(te))

            st = time.time()
            self.in_stream.write(samples)
            # print("Write time: {}".format(time.time() - st))
