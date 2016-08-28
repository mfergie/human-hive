"""
Defines all the sources. Each source controls playback in a different manner.
They provide chunks of frames for playback.
"""
import numpy as np
from humanhive import utils, hive, swarm, samplestream

class SourceBank:
    """
    Manages the sources that will be played. These are created externally
    and added in.
    """

    def __init__(self):
        self.sources = []

    def add_source(self, source):
        self.sources.append(source)


class SwarmSource:
    """
    This is the source for a normal swarm. Sample plays as if it is moving
    around the space.
    """

    def __init__(self,
                 audio_data,
                 n_channels,
                 sample_rate,
                 volume=1.0):

        self.sample = samplestream.SampleStream(audio_data)
        self.n_channels=n_channels

        self.volume = volume
        self.sample_rate = sample_rate
        # Create swarm volume controller
        self.hive_radius = 3
        self.n_hives = n_channels
        self.hives = hive.generate_hive_circle(
            n_hives=self.n_hives, hive_radius=self.hive_radius)

        self.swarm = swarm.SwarmLinear(
            hives=self.hives,
            swarm_speed=0.1,
            sample_rate=self.sample_rate)



    def get_frames(self, n_frames):

        samples = np.asarray(self.sample.retrieve_samples(n_frames), np.float32)

        samples_all_channels = samplestream.copy_n_channels(samples, self.n_channels)
        swarm_volumes = self.swarm.sample_swarm_volumes(n_frames)
        # print("Swarm volumes: {}".format(swarm_volumes[0]))
        samples_all_channels *= swarm_volumes

        # Final volume
        samples_all_channels *= self.volume
        return samples_all_channels



class OccasionalSource:
    """
    This source will play a sample through a random hive at fixed time.
    Intervals.

    repeat_period is the time in seconds to wait between plays
    """

    def __init__(self,
                 audio_data,
                 n_channels,
                 sample_rate,
                 repeat_period=15*60, #default 15 mins
                 volume=1.0):

        self.audio_data = audio_data
        self.n_audio_frames = len(self.audio_data)
        self.n_channels=n_channels

        self.volume = volume
        self.sample_rate = sample_rate

        self.current_frame = None
        self.n_frames_between_play = repeat_period * sample_rate
        self.frames_till_next_play = self.n_frames_between_play
        self.channel_to_play = 0

    def get_frames(self, n_frames):

        # Prepare a buffer of zeros to return.
        out_data = np.zeros((n_frames, self.n_channels), dtype=np.int16)

        print("current_frame: {}, frames_till_next_play: {}".format(
            self.current_frame, self.frames_till_next_play  ))

        if self.current_frame is None:
            self.frames_till_next_play -= n_frames
            if self.frames_till_next_play <= 0:
                # It's time to play the sample
                self.current_frame = 0
                self.channel_to_play = np.random.randint(self.n_channels)

        elif self.current_frame <= self.n_audio_frames:
            n_frames_to_take = min(n_frames, self.n_audio_frames - self.current_frame)
            out_data[:n_frames_to_take, self.channel_to_play] = (
                self.audio_data[
                    self.current_frame:self.current_frame + n_frames_to_take])
            # Advance through sample
            self.current_frame += n_frames

            if n_frames_to_take < n_frames:
                # We've finished the sample, reset
                self.current_frame = None
                self.frames_till_next_play = self.n_frames_between_play

        out_data_fp = np.asarray(out_data, dtype=np.float32) * self.volume
        out_data = np.asarray(out_data_fp, dtype=np.int16)

        return out_data
