"""
Contains the main human hive class for operation.
"""
import sys
import time
import multiprocessing
from multiprocessing import Queue, Process
from threading import Thread
import numpy as np
import pyaudio
from . import samplestream, swarm, hive, utils
from .playback import PlaybackQueueProducer
from .recording import Recording
from .sources import SourceBank

if "linux" in sys.platform:
    # If using linux, use the ALSA module directly
    from .audio_interface_alsa import AudioInterface
else:
    from .audio_interface import AudioInterface

def playback_consumer(playback_queue,
                      recording_queue,
                      n_channels,
                      sample_rate,
                      sample_width,
                      n_frames_per_chunk,
                      output_device_id,
                      input_device_id=None):
    """
    Creates a PlaybackQueueConsumer and audio interface and configured to
    retrieve and send samples to the playback and recording queues respectively.
    This function then enters a blocking loop to process audio data.
    """

    proc_name = multiprocessing.current_process().name
    print("playback_consumer: Running on {}".format(proc_name))

    audio_interface = AudioInterface(
        playback_queue,
        recording_queue,
        n_channels,
        sample_rate,
        sample_width,
        output_device_id,
        input_device_id,
        n_frames_per_chunk)

    print("playback_consumer: Starting audio stream in {}".format(proc_name))
    audio_interface.start_stream()
    print("playback_consumer: Calling Audio Interface.run()")
    audio_interface.run()


def recording_consumer(recording_queue, sample_rate):
    """
    Sets up the recording consumer.
    """
    proc_name = multiprocessing.current_process().name
    print("recording_consumer: Running on {}".format(proc_name))

    recording = Recording(
        None, recording_queue, 4*sample_rate)
    print("Entering recording.run()")
    recording.run()


class HumanHive:
    """
    HumanHive provides the overall access and control to the human hive system.
    """

    def __init__(self,
                 n_channels=2,
                 sample_rate=44100,
                 sample_width=2,
                 output_device_id=0,
                 input_device_id=0,
                 master_volume=1.0):

        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.sample_width = sample_width

        self.source_bank = SourceBank()

        self.chunks_queue_size = 100

        ctx = multiprocessing.get_context('spawn')

        self.playback_queue = ctx.Queue(self.chunks_queue_size)
        self.recording_queue = ctx.Queue(self.chunks_queue_size)

        self.n_frames_per_chunk = 1024

        self.playback_producer = PlaybackQueueProducer(
            self.source_bank,
            self.playback_queue,
            self.n_channels,
            self.sample_rate,
            self.n_frames_per_chunk,
            master_volume=master_volume)

        self.audio_interface_process = ctx.Process(
            target=playback_consumer,
            args=(
                self.playback_queue,
                None, #self.recording_queue,
                self.n_channels,
                self.sample_rate,
                self.sample_width,
                self.n_frames_per_chunk,
                output_device_id,
                input_device_id))

        self.recording_process = ctx.Process(
            target=recording_consumer,
            args=(
                self.recording_queue,
                self.sample_rate))

        print("Launching processes")
        self.audio_interface_process.daemmon = True
        self.audio_interface_process.start()

        self.recording_process.daemmon = True
        self.recording_process.start()



    def run(self):
        """
        Enter main HumanHive loop.
        """
        self.playback_producer.run()
