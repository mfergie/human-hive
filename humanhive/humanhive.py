"""
Contains the main human hive class for operation.
"""
import numpy as np
import pyaudio
from . import samplestream, swarm, hive, utils

class HumanHive:
    """
    HumanHive provides the overall access and control to the human hive system.
    """

    def __init__(self,
                 swarm_samples_dir,
                 recorded_samples_dir=None,
                 n_channels=2,
                 sample_rate=44100,
                 sample_width=2,
                 device_id=0):

        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width

        self.sample_bank = SampleBank(swarm_samples_dir, recorded_samples_dir)
        self.recording = Recording(self.sample_bank)
        self.playback = Playback(
            self.sample_bank, self.n_channels, self.sample_rate)
        self.audio_interface = AudioInterface(
            self.playback,
            self.recording,
            self.n_channels,
            self.sample_rate,
            self.sample_width,
            device_id)



    def start_stream(self):
        self.audio_interface.start_stream()


    def close_stream(self):
        self.audio_interface.close_stream()

    def is_active(self):
        return self.audio_interface.is_active()

class Playback:
    """
    Manages the playback of sounds. Keeps active samples and controls volumes
    etc.
    """
    def __init__(self,
                 sample_bank,
                 n_channels,
                 sample_rate):

        self.sample_bank = sample_bank

        self.n_channels = n_channels
        self.sample_rate = sample_rate

        # For now, use a fixed sample
        self.sample = samplestream.SampleStream(self.sample_bank.swarm_samples[0])

        # Create swarm volume controller
        self.hive_radius = 3
        self.n_hives = n_channels
        self.hives = hive.generate_hive_circle(
            n_hives=self.n_hives, hive_radius=self.hive_radius)
        self.swarm = swarm.SwarmLinear(
            hives=self.hives,
            swarm_speed=0.1,
            sample_rate=self.sample_rate)

    def retrieve_samples(self, frame_count):

        samples = np.asarray(self.sample.retrieve_samples(frame_count), np.float32)

        samples_stereo = samplestream.copy_n_channels(samples, self.n_channels)
        swarm_volumes = self.swarm.sample_swarm_volumes(frame_count)
        print("Swarm volumes: {}".format(swarm_volumes[0]))
        samples_stereo *= swarm_volumes


        samples_stereo *= 0.5
        return np.asarray(samples_stereo, np.int16)




class Recording:
    """
    Takes the input data from the sound interface, segments them into samples
    and then directs these samples to a sample bank.
    """

    def __init__(self, sample_bank):
        self.sample_bank = sample_bank

        # Stores a list of frames which make up the current sample. Initialised
        # to None to indicate that there is no current sample being recorded.
        self.current_sample = None

        # Stores the volume of the last sub-frame picked up by process_audio()
        # Used to threshold volume when segmenting audio. Initialise to None
        # to allow setting at initial levels. n_ambient_chunks stores the
        # number of ambient chunks used to compute the average
        self.ambient_volume = None
        self.n_ambient_chunks = 0

    def process_audio(self, in_data, frame_count):
        """
        Processes incoming audio data. Segments when a voice is detected and
        records sample. This is then saved to the sample_bank.
        """
        # in_data = np.frombuffer(in_data, dtype=np.int16)
        #
        # if self.current_sample is None:
        #     self.update_ambient_volume(in_data)




    def update_ambient_volume(self, in_data):
        """
        Updates the ambient volume
        """
        if self.ambient_volume is None:
            self.ambient_volume = utils.compute_audio_volume(in_data)
        else:
            existing_ambient_volume = (
                self.ambient_volume *
                (self.n_ambient_chunks / (self.n_ambient_chunks + 1)))
            current_contribution = (
                utils.compute_audio_volume(in_data) / (self.n_ambient_chunks + 1))
            self.ambient_volume = existing_ambient_volume + current_contribution

class AudioInterface:
    """
    Manages the sound interface. This manages the main callback for the audio
    interface and delegates behaviour to the Playback and Recording modules.
    """

    def __init__(self,
                 playback,
                 recording,
                 n_channels,
                 sample_rate,
                 sample_width,
                 device_id):
        self.playback = playback
        self.recording = recording
        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width

        # Initialise pyaudio interface
        self.p = pyaudio.PyAudio()

        print("Device parameters for device with id: {}\n{}".format(
            device_id, self.p.get_device_info_by_index(device_id)))

        self.stream = self.p.open(
            format=self.p.get_format_from_width(2),
            channels=self.n_channels,
            rate=self.sample_rate,
            output_device_index=device_id,
            # input=True,
            output=True,
            stream_callback=self.audio_callback)
        print("Finished initialising audio")


    def audio_callback(self, in_data, frame_count, time_info, status):

        # Send recording data
        self.recording.process_audio(in_data, frame_count)

        # Get output audio
        samples = self.playback.retrieve_samples(frame_count)

        return (samples, pyaudio.paContinue)


    def start_stream(self):
        self.stream.start_stream()


    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()


    def is_active(self):
        return self.stream.is_active()



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
