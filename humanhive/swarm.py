"""Module for managing swarm positions"""
import math
import numpy as np

class CosSinSwarm:
    """
    A toy module for doing 2 channel volumes using cos/sin functions.
    """
    def __init__(self, sample_rate):

        self.sample_rate = sample_rate
        self.start_theta = 0
        self.period = 20

    def sample_swarm_volumes(self, frame_count):
        end_theta = (self.start_theta +
            ((frame_count / (self.sample_rate*self.period)) * 2*math.pi))
        theta = np.linspace(self.start_theta, end_theta, frame_count)
        self.start_theta = end_theta
        left_vol = np.cos(theta)
        right_vol = np.sin(theta)

        return np.hstack((left_vol[:,np.newaxis], right_vol[:,np.newaxis]))


class Swarm:

    def __init__(hives, swarm_speed):
        """
        Initialise a swarm.

        Parameters
        ----------
        hives: array_like, (H, 2)
            An array containing the 2D positions of each hive.
            H denotes the number of hives.
        swarm_speed: float
            The speed that the swarm will travel.
        """
        self.hives = hives
        self.swarm_speed = swarm_speed

        # Now initialise position
        self.swarm_position = None# ...

        assert False, "Needs completing"

    def sample_swarm_positions(duration, sample_rate):
        """
        Samples the position of a swarm for a given duration and
        sample rate. Updates the internal state of the object
        with the new swarm position such that subsequent calls
        will progress the swarm on its path.

        Parameters
        ----------
        duration: float
            The duration in seconds for which to generate the samples.
        sample_rate: int
            The number of samples to generate a second.

        Returns
        -------
        positions: array_like, (N, 2)
            Returns N = duration * sample_rate samples for the position
            of the swarm.
        """

        # Compute the distance to the next hive.

        # If the swarm will reach the hive within this request, randomly pick the next hive

        # Generate position samples from the initial position, to the destination hive.

        assert False, "Not implemented"
