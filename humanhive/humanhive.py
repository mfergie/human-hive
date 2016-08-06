"""
Contains the main human hive class for operation.
"""
import time
from multiprocessing import Queue, Process
from threading import Thread
import numpy as np
import pyaudio
from . import samplestream, swarm, hive, utils

def playback_consumer(playback_queue,
                      recording_queue,
                      n_channels,
                      sample_rate,
                      sample_width,
                      device_id):
    """
    Creates a PlaybackQueueConsumer and audio interface and configured to
    retrieve and send samples to the playback and recording queues respectively.
    This function then enters a blocking loop to process audio data.
    """
    playback_consumer = PlaybackQueueConsumer(playback_queue)

    audio_interface = AudioInterface(
        playback_consumer,
        recording_queue,
        n_channels,
        sample_rate,
        sample_width,
        device_id)

    print("Starting audio stream")
    audio_interface.start_stream()
    print("Calling Audio Interface.run()")
    audio_interface.run()

class HumanHive:
    """
    HumanHive provides the overall access and control to the human hive system.
    """

    def __init__(self,
                 n_channels=2,
                 sample_rate=44100,
                 sample_width=2,
                 device_id=0,
                 master_volume=1.0):

        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width

        self.source_bank = SourceBank()

        self.recording = Recording(self.source_bank, 4*sample_rate)

        self.chunks_queue_size = 100

        self.playback_queue = Queue(self.chunks_queue_size)
        self.recording_queue = None

        self.n_samples_per_chunk = 1024

        self.playback_producer = PlaybackQueueProducer(
            self.source_bank,
            self.playback_queue,
            self.n_channels,
            self.sample_rate,
            self.n_samples_per_chunk,
            master_volume=master_volume)

        self.audio_interface_process = Process(
            target=playback_consumer,
            args=(
                self.playback_queue,
                self.recording_queue,
                self.n_channels,
                self.sample_rate,
                self.sample_width,
                device_id))

        self.audio_interface_process.start()


    def run(self):
        """
        Enter main HumanHive loop.
        """
        self.playback_producer.run()


class Playback:
    """
    Manages the playback of sounds. Keeps active samples and controls volumes
    etc.
    """
    def __init__(self,
                 source_bank,
                 n_channels,
                 sample_rate,
                 master_volume):

        self.source_bank = source_bank

        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.master_volume = master_volume


    def retrieve_samples(self, n_frames):
        samples = np.zeros(
            (n_frames, self.n_channels), dtype=np.float)
        for source in self.source_bank.sources:
            samples += source.get_frames(n_frames)

        samples *= self.master_volume
        return np.asarray(samples, np.int16)


class PlaybackQueueProducer:
    """
    Keeps a queue filled with audio samples.
    """
    def __init__(self,
                 source_bank,
                 chunks_queue,
                 n_channels,
                 sample_rate,
                 n_samples_per_chunk,
                 master_volume=1.0):

        self.source_bank = source_bank
        self.chunks_queue = chunks_queue

        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.n_samples_per_chunk = n_samples_per_chunk
        self.master_volume = master_volume


    def run(self):
        """
        Generates samples and inserts them into queue.
        """
        while True:
            print("Producing")
            samples = np.zeros(
                (self.n_samples_per_chunk, self.n_channels), dtype=np.float)
            for source in self.source_bank.sources:
                print(samples)
                samples += source.get_frames(self.n_samples_per_chunk)

            samples *= self.master_volume

            # Insert into queue, block if queue fills up.
            self.chunks_queue.put(samples, block=True)


class PlaybackQueueConsumer:
    """
    This is a class that meets the playback interface. Instead of computing
    samples online it will retrieve them from a shared queue populated by a
    PlaybackQueueProducer.
    """
    def __init__(self,
                 chunks_queue):
        self.chunks_queue = chunks_queue

    def retrieve_samples(self, n_frames):
        print("Consuming")
        samples = self.chunks_queue.get(block=True)
        print(samples)
        return samples

class Recording:
    """
    Takes the input data from the sound interface, segments them into samples
    and then directs these samples to a sample bank.
    """

    def __init__(self, sample_bank, n_samples_buffer):
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

        self.n_samples_buffer = n_samples_buffer

        # Stores past samples for capturing recorded data when threshold
        # lies between calls to process_audio
        self.sample_buffer = []

        # Stores changing volumes over time for analysis
        self.volume_buffer = []

    def process_audio(self, in_data, frame_count):
        """
        Processes incoming audio data. Segments when a voice is detected and
        records sample. This is then saved to the sample_bank.
        """

        # in_data = np.frombuffer(in_data, dtype=np.int16)
        #
        # if self.current_sample is None:
        #     self.update_ambient_volume(in_data)
        #
        # print(self.ambient_volume)
        #
        # self.update_sample_buffers(in_data, frame_count)

        # Turn volumes into threshold crossings

        # If there's a threshold crossing with no opposing return within the
        # specified time limit, start recording.

        # If the recording has passed a minimum length, and there is a down
        # threshold which stays down for a specified time stop recording.

        # Save the recorded data somewhere

        # Send this off to the SourceBank for adding into the mix.



    def update_sample_buffers(self, in_data, frame_count):

        # Check whether to discard oldest audio and volume samples. This assumes
        # that the frame_count is always consistent
        if len(sample_buffer) > (self.n_samples_buffer / frame_count):
            self.sample_buffer.pop(0)
            self.volume_buffer.pop(0)

        self.sample_buffer.append(in_data)
        self.volume_buffer.append(
            utils.compute_audio_volume_per_frame(in_data))

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
            #stream_callback=self.audio_callback
            )
        print("Finished initialising audio")


    def audio_callback(self, in_data, frame_count, time_info, status):
        st = time.time()
        # Send recording data
        if self.recording_queue is not None:
            self.recording_queue.put((in_data, frame_count))

        # Get output audio
        samples = self.playback.retrieve_samples(frame_count)

        te = time.time() - st
        print("Time elapsed: {}".format(te))
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
            self.stream.write(data, self.frame_count)



class SourceBank:
    """
    Manages the sources that will be played. These are created externally
    and added in.
    """

    def __init__(self):
        self.sources = []

    def add_source(self, source):
        self.sources.append(source)
