"""
Contains the main human hive class for operation.
"""
import pyaudio

class HumanHive:
    """
    HumanHive provides the overall access and control to the human hive system.
    """

    def __init__(self):
        assert False, "Unfinished"


class Playback:
    """
    Manages the playback of sounds. Keeps active samples and controls volumes
    etc.
    """
    def __init__(self, sample_bank):
        self.sample_bank = sample_bank

class Recording:
    """
    Takes the input data from the sound interface, segments them into samples
    and then directs these samples to a sample bank.
    """

    def __init__(self, sample_bank):
        self.sample_bank = sample_bank

class SoundInterface:
    """
    Manages the sound interface. This manages the main callback for the audio
    interface and delegates behaviour to the Playback and Recording modules.
    """

    def __init__(self,
                 playback,
                 recording,
                 n_channels,
                 sample_rate,
                 sample_width):
        self.playback = playback
        self.recording = recording
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width

        # Initialse pyaudio interface
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format=self.p.get_format_from_width(2),
            channels=self.n_channels,
            rate=self.sample_rate,
            input=True,
            output=True,
            stream_callback=self.audio_callback)

        self.stream.start_stream()


    def audio_callback(self, in_data, frame_count, time_info, status):
        assert False, "Unimplemented"


    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()



class SampleBank:
    """
    Manages the samples that will be played.
      - Loads sets of samples from disk.
      - Stores recorded samples
    """

    def __init__(self,
                 swarm_samples_dir=None,
                 recorded_samples_dir=None):

        # Load samples
        if swarm_samples_dir is not None:
            self.swarm_samples = samplestream.load_samples_from_dir(
                swarm_samples_dir)
        else:
            self.swarm_samples = []

        if recorded_samples_dir is not None:
            self.recorded_samples = samplestream.load_samples_from_dir(
                recorded_samples_dir)
        else:
            self.recorded_samples = []
