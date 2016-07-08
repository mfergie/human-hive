"""Module for managing swarm positions"""
import math
import numpy as np
from sklearn.metrics.pairwise import rbf_kernel

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

    def __init__(self, r, hives, swarm_speed, sample_rate):
        """
        Initialise a swarm.

        Parameters
        ----------
        r: float
            If the hives are in a circular arrangement, this
            is the radius of the circle in m.
        hives: array_like, (H, 2)
            An array containing the 2D positions of each hive.
            H denotes the number of hives.
        swarm_speed: float
            The speed that the swarm will travel.
        sample_rate: int
            The sample rate.
        """
        self.r = r
        self.hives = hives
        self.swarm_speed = swarm_speed
        print(swarm_speed)
        self.swarm_speed_rad = swarm_speed/r
        self.sample_rate = sample_rate

        # Now initialise position
        #
        # Perhaps the simplest way is to give the swarm position as angle
        # from some reference point
        self.swarm_position = 0

        # assert False, "Needs completing"

    def sample_swarm_positions_rand(self, n_samples):
        """
        Samples the position of a swarm as it moves around the
        circle at random for a given duration and sample rate.
        Updates the internal state of the object with the new
        swarm position such that subsequent calls will progress
        the swarm on its path.

        Parameters
        ----------
        duration: float
            The duration in seconds for which to generate the samples.
        n_samples: int
            The number of samples to generate.

        Returns
        -------
        positions: array_like, (N, 2)
            Returns N = duration * sample_rate samples for the position
            of the swarm. Position is given by the angle of the swarm
        """

        ##########################################
        # NOTE: I THINK THIS SHOULD BE MORE ROBUST IF WE INPUT SAMPLE RATE AND
        # NUMBER OF SAMPLES, RATHER THAN DURATION.
        ##########################################

        # Give options for how long the hive can linger for
        min_linger_time = 3 # s
        max_linger_time = 30 # s
        linger_options = range(min_linger_time, max_linger_time)

        # Choose a random hive to begin at and update position
        hive_no = np.random.randint(7)
        self.swarm_position = np.pi/12 + np.pi*hive_no/6

        total_samples = n_samples
        s_counter = 0       # Sample counter
        positions = np.empty((total_samples, 2))

        print("Shape of positions is ", np.shape(positions))
        print("Total number of samples is ", total_samples)

        increment = self.swarm_speed_rad/self.sample_rate
        tolerance = increment

        while s_counter < total_samples:
            # Allocate positions while hive is stationary
            t_stay = linger_options[np.random.randint(len(linger_options))]
            sample_num = t_stay * self.sample_rate
            new_s_counter = s_counter + sample_num

            current_position = np.array([[self.r*np.cos(self.swarm_position), \
                self.r*np.sin(self.swarm_position)]])

            if s_counter + sample_num < total_samples:
                positions[s_counter:new_s_counter, :] = \
                                       np.full([sample_num,2], current_position)
            else:
                positions[s_counter:,:] = \
                          np.full([total_samples-s_counter,2], current_position)

            # Choose the next hive at random
            hive_no = np.random.randint(7)
            destination_angle = np.pi/12 + np.pi*hive_no/6

            # Swarm direction,
            # Go either anticlockwise (+1) or clockwise (-1)
            s_dir = 2 * np.random.randint(2) - 1

            # Allocate positions while moving
            while (new_s_counter < total_samples and
                    self.swarm_position != destination_angle):
                # Increment swarm position
                self.swarm_position = self.swarm_position + s_dir*increment
                current_position = (
                    np.array([[self.r*np.cos(self.swarm_position),
                    self.r*np.sin(self.swarm_position)]]))

                # Update positions array
                positions[new_s_counter, :] = current_position

                new_s_counter += 1

                pos = (
                    self.swarm_position -
                    np.floor(self.swarm_position/(2*np.pi)) * 2 * np.pi)
                if abs(destination_angle - pos) < tolerance:
                    self.swarm_position = destination_angle

            s_counter = new_s_counter

        return positions


def hive_volumes(hives, swarm_positions, sigma=1):
    """
    Computes the volume at each hive based on the swarm position.

    Parameters
    ----------
    hives: array_like, (H, 2)
        An array containing the 2D positions of each hive.
        H denotes the number of hives.
    swarm_positions: (N, 2)
        The position of the swarm at each sample.

    Returns
    -------
    hive_volumes: array_like, (H, N)
        The volume for each hive at each sample.
    """
    return rbf_kernel(hives, swarm_positions, gamma=1)
