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
from .mixer import Mixer
from .loopback import Loopback

if "linux" in sys.platform:
    # If using linux, use the ALSA module directly
    from .audio_interface_alsa import AudioInterface
else:
    from .audio_interface import AudioInterface

def playback_consumer(playback_queue,
                      recording_queue,
                      loopback_queue,
                      n_channels,
                      sample_rate,
                      sample_width,
                      n_frames_per_chunk,
                      output_device_id,
                      input_device_id=None,
                      mpctx=None):
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
        loopback_queue,
        n_channels,
        sample_rate,
        sample_width,
        output_device_id,
        input_device_id,
        n_frames_per_chunk,
        mpctx=mpctx)

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

def loopback_process(loopback_queue,
                     loopback_mixer_queue,
                     n_channels_in,
                     n_channels_out):
    """
    Runs a loopback object
    """
    loopback = Loopback(
        loopback_queue, loopback_mixer_queue, n_channels_in, n_channels_out)

    loopback.run()

def mixer_process(mixer_in_queues,
                  mixer_out_queue):
    mixer = Mixer(mixer_in_queues, mixer_out_queue)
    mixer.run()

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
        self.loopback_queue = ctx.Queue(self.chunks_queue_size)
        self.loopback_mixer_queue = ctx.Queue(self.chunks_queue_size)
        self.playback_mixer_queue = ctx.Queue(self.chunks_queue_size)
        self.mixer_out_queue = ctx.Queue(self.chunks_queue_size)

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
                self.mixer_out_queue,
                self.recording_queue,
                self.loopback_queue,
                self.n_channels,
                self.sample_rate,
                self.sample_width,
                self.n_frames_per_chunk,
                output_device_id,
                input_device_id,
                ctx))

        self.recording_process = ctx.Process(
            target=recording_consumer,
            args=(
                self.recording_queue,
                self.sample_rate))

        self.loopback_process = ctx.Process(
            target=loopback_process,
            args=(
                self.loopback_queue,
                self.loopback_mixer_queue,
                2,
                self.n_channels))

        self.mixer_process = ctx.Process(
            target=mixer_process,
            args=(
                [self.loopback_mixer_queue, self.playback_queue],
                self.mixer_out_queue))

        print("Launching processes")
        self.audio_interface_process.daemmon = True
        self.audio_interface_process.start()

        self.recording_process.daemmon = True
        self.recording_process.start()

        self.loopback_process.daemmon = True
        self.loopback_process.start()

        self.mixer_process.daemmon = True
        self.mixer_process.start()

    def run(self):
        """
        Enter main HumanHive loop.
        """
        print("HH.run()")
        self.playback_producer.run()
