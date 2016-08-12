import pyaudio
import time
import numpy as np


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
                 input_device_id,
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

        output_device_id = int(output_device_id)
        input_device_id = int(input_device_id)


        print("Output device parameters for device with id: {}\n{}".format(
            output_device_id, self.p.get_device_info_by_index(output_device_id)))
        print("Input device parameters for device with id: {}\n{}".format(
            input_device_id, self.p.get_device_info_by_index(input_device_id)))

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

        # Loopback stuff
        self.loopback_stream = self.stream
        self.input_stream = self.stream

        self.loopback_channels_left = [i for i in range(0, self.n_channels//2)]
        self.loopback_channels_right = [i for i in range(self.n_channels//2, self.n_channels)]

    def start_stream(self):
        self.stream.start_stream()


    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()


    def is_active(self):
        return self.stream.is_active()


    def loopback_audio(self):
        """
        Reads input from the loopback device, and then prepares it for output
        """
        loopback_buffer = self.loopback_stream.read(
            self.frame_count, exception_on_overflow=False)

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
        # Send recording data
        if self.recording_queue is not None:
            # in_data = self.stream.read(self.frame_count, exception_on_overflow=False)
            # self.recording_queue.put((self.frame_count, in_data), block=False)
            pass

        loopback_samples = self.loopback_audio()

        # Get output audio
        # samples = self.playback.get()

        # Add in the loopback samples
        samples = loopback_samples

        self.stream.write(samples, self.frame_count, exception_on_underflow=False)


    def run(self):
        while True:
            self.process_audio_chunk()
