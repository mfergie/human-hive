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
                 loopback_queue,
                 n_channels,
                 sample_rate,
                 sample_width,
                 output_device_id,
                 input_device_id,
                 frame_count=1024,
                 mpctx=None):
        self.playback = playback
        self.recording_queue = recording_queue
        self.loopback_queue = loopback_queue
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


    def start_stream(self):
        self.stream.start_stream()


    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()


    def is_active(self):
        return self.stream.is_active()


    def process_audio_chunk(self):
        print("PAC AI")
        # Send recording data
        if self.recording_queue is not None:
            # in_data = self.stream.read(self.frame_count, exception_on_overflow=False)
            # self.recording_queue.put((self.frame_count, in_data), block=False)
            pass

        if self.loopback_queue is not None:
            in_data = np.frombuffer(
                self.stream.read(self.frame_count, exception_on_overflow=False),
                dtype=np.uint16).reshape(-1, 2)
            self.loopback_queue.put(in_data, block=False)

        # Get output audio
        samples = self.playback.get()

        self.stream.write(samples, self.frame_count, exception_on_underflow=False)


    def run(self):
        while True:
            print("AI.run()")
            self.process_audio_chunk()
