import time
import alsaaudio
import numpy as np
from threading import Thread


class AudioInterfaceSingleDevice:
    """
    Processes audio from a single device.
    """

    def __init__(self,
                 audio_queue,
                 pcm_type,
                 n_channels,
                 sample_rate,
                 sample_width,
                 device_id,
                 frame_count):

        self.audio_queue = audio_queue
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.frame_count = frame_count

        self.stream = alsaaudio.PCM(
            type=pcm_type,
            #mode=alsaaudio.PCM_NONBLOCK,
            device=device_id)
        self.stream.setchannels(2)
        self.stream.setrate(self.sample_rate)
        self.stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.stream.setperiodsize(self.frame_count)
        print("stream card: {}".format(self.stream.cardname()))


    def process_audio_chunk(self):

        if self.stream.pcmtype() == alsaaudio.PCM_CAPTURE:
            # Input stream
            in_data = self.stream.read()
            if in_data[0]:
                audio_data = np.frombuffer(
                    in_data[1], dtype=np.int16).reshape(-1, 2)
                self.audio_queue.put(audio_data)

        else:
            # Output stream
            samples = self.audio_queue.get()
            self.stream.write(samples)


    def run(self):
        while True:
            self.process_audio_chunk()


def audio_interface_process(audio_queue,
                            pcm_type,
                            n_channels,
                            sample_rate,
                            sample_width,
                            device_id,
                            frame_count):
    audio_interface = AudioInterfaceSingleDevice(
        audio_queue,
        pcm_type,
        n_channels,
        sample_rate,
        sample_width,
        device_id,
        frame_count)
    audio_interface.run()


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
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.frame_count = frame_count

        print("frame_count: {}".format(frame_count))

        print("available cards: {}".format(alsaaudio.cards()))
        print("available PCMs: {}".format(alsaaudio.pcms()))

        self.playback_process = Thread(
            target=audio_interface_process,
            args=(
                playback_queue,
                alsaaudio.PCM_PLAYBACK,
                n_channels,
                sample_rate,
                sample_width,
                output_device_id,
                frame_count))

        self.loopback_process = Thread(
            target=audio_interface_process,
            args=(
                loopback_queue,
                alsaaudio.PCM_PLAYBACK,
                2,
                sample_rate,
                sample_width,
                input_device_id,
                frame_count))


        print("Starting recording processes")
        # Start input processes first, and let the buffers pre-fill
        self.loopback_process.daemon = True
        self.loopback_process.start()
        time.sleep(0.1)


        print("Starting playback process")
        self.playback_process.daemmon = True
        self.playback_process.start()


    def start_stream(self):
        pass


    def run(self):
        while True:
            # Doesn't need to do anything. So just sleep
            time.sleep(1)
