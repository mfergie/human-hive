"""
Defines all the sources. Each source controls playback in a different manner.
They provide chunks of frames for playback.
"""
import numpy as np
from humanhive import utils, hive, swarm, samplestream

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
