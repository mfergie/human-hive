import pyaudio
import time


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
                 output_device_id,
                 input_device_id=None,
                 frame_count=1024):
        self.playback = playback
        self.recording_queue = recording_queue
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.frame_count = frame_count

        print("frame_count: {}".format(frame_count))

        # Initialise pyaudio interface
        self.p = pyaudio.PyAudio()

        print("Output device parameters for device with id: {}\n{}".format(
            output_device_id, self.p.get_device_info_by_index(output_device_id)))
        print("Input device parameters for device with id: {}\n{}".format(
            input_device_id, self.p.get_device_info_by_index(input_device_id)))

        if input_device_id is None:
            input_device_id = output_device_id

        self.stream = self.p.open(
            format=self.p.get_format_from_width(2),
            channels=self.n_channels,
            rate=self.sample_rate,
            output_device_index=output_device_id,
            input_device_index=input_device_id,
            input=True,
            output=True,
            #stream_callback=self.audio_callback,
            )
        print("Finished initialising audio")


    def audio_callback(self, in_data, frame_count, time_info, status):
        st = time.time()
        # Send recording data
        if self.recording_queue is not None:
            self.recording_queue.put((in_data, frame_count))

        # Get output audio
        samples = self.playback.get()

        te = time.time() - st
        # print("Time elapsed: {}".format(te))

        return (samples, pyaudio.paContinue)


    def start_stream(self):
        self.stream.start_stream()


    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()


    def is_active(self):
        return self.stream.is_active()

    def run(self):
        while True:
            (data, status) = self.audio_callback(
                None, self.frame_count, None, None)
            st = time.time()
            self.stream.write(data, self.frame_count, exception_on_underflow=False)
            # print("Write time: {}".format(time.time() - st))
