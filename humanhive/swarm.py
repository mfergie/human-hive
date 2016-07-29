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


class SwarmLinear:
    def __init__(self,
                 hives,
                 swarm_speed,
                 sample_rate,
                 p_change_direction=0.2,
                 p_jump_hives=0.1):
        """
        Initialise a swarm.

        Parameters
        ----------
        hives: array_like, (H, 2)
            An array containing the 2D positions of each hive.
            H denotes the number of hives.
        swarm_speed: float
            The speed that the swarm will travel. This is given in units/second
            where the units are the same as those used for the hive positions.
        sample_rate: int
            The sample rate.
        """
        self.hives = np.asarray(hives)
        self.n_hives = len(hives)
        self.swarm_speed = swarm_speed
        # Compute how far the swarm should travel per frame
        self.swarm_speed_upf = self.swarm_speed / sample_rate
        self.sample_rate = sample_rate

        self.p_change_direction = p_change_direction
        self.p_jump_hives = p_jump_hives

        # Initialise movement. Set initial position to hive 0, and set them off
        # towards hive 1
        self.swarm_position = self.hives[0]
        self.destination_hive = 1

        # n_linger_frames stores the number of frames that the swarm has remaining
        # to linger at the current position.
        self.n_linger_frames = 0

        # Stores the direction of the swarm movement as +1 or -1. This is
        # randomly sampled from p_change_direction
        self.swarm_direction = 1

    def sample_swarm_positions(self, n_samples):
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

        # Compute the frame index that movement will start at.
        if self.n_linger_frames > n_samples:
            # Still lingering, set movement_start_frame to n_samples
            movement_start_frame = n_samples
        else:
            movement_start_frame = self.n_linger_frames


        # Compute the frame index that movement will end at
        swarm_destination_position = self.hives[self.destination_hive]
        destination_vector = (
            swarm_destination_position - self.swarm_position)

        # movement_per_frame_vector gives the offset for each frame of
        # movement.
        movement_per_frame_vector = (
            (destination_vector / np.linalg.norm(destination_vector)) *
            self.swarm_speed_upf)

        # Compute the frame that we would reach destination by projecting
        # the destination point onto the movement vector
        destination_frame = int(np.ceil(
            (swarm_destination_position[0] - self.swarm_position[0]) /
            movement_per_frame_vector[0]))



        n_remaining_frames = n_samples - movement_start_frame

        if destination_frame > n_remaining_frames:
            movement_end_frame = n_samples
        else:
            movement_end_frame = movement_start_frame + destination_frame

        # Now set the positions
        positions = np.zeros((n_samples, 2), dtype=np.float32)

        # Movement start
        positions[:movement_start_frame] = self.swarm_position[np.newaxis,:]

        # Movement middle
        frame_indices = np.arange(1, (movement_end_frame - movement_start_frame) + 1)
        relative_positions = (
            movement_per_frame_vector[np.newaxis,:] * frame_indices[:,np.newaxis])
        positions[movement_start_frame:movement_end_frame] = (
            relative_positions + self.swarm_position)

        # Movement end, copy last movement position to finish
        positions[movement_end_frame:] = positions[movement_end_frame-1]

        ###
        # Now update internal state
        ###
        self.swarm_position = positions[-1]
        if movement_end_frame < n_samples:
            # We reached destination, sample new destination hive

            # Change direction?
            if np.random.rand(1)[0] < self.p_change_direction:
                # Yes, change direction
                self.swarm_direction *= -1
                print("Swapping direction: {}".format(self.swarm_direction))
            self.destination_hive = (self.destination_hive + self.swarm_direction) % self.n_hives

            # Jump hives?
            if np.random.rand(1)[0] < self.p_jump_hives:
                # Yes, generate a random destination hive
                self.destination_hive = np.random.randint(self.n_hives)
                print("Jumping hives, new destination: {}".format(
                    self.destination_hive))

            # Sample a linger time
            self.n_linger_frames = (
                3 * self.sample_rate - (n_samples - movement_end_frame))

            print("swarm_position: {}, destination_hive: {}, n_linger_frames: {}".format(
                self.swarm_position, self.destination_hive, self.n_linger_frames))

        if movement_start_frame > 0:
            self.n_linger_frames -= movement_start_frame


        return positions

    def sample_swarm_volumes(self, n_samples):
        swarm_positions = self.sample_swarm_positions(n_samples)
        # print(swarm_positions)
        # print("Position: {}".format(swarm_positions[0]), end=", ")
        return hive_volumes(self.hives, swarm_positions)


class Swarm:

    def __init__(self, hive_radius, hives, swarm_speed, sample_rate):
        """
        Initialise a swarm.

        Parameters
        ----------
        hive_radius: float
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
        self.hive_radius = hive_radius
        self.hives = hives
        self.n_hives = len(hives)
        self.swarm_speed = swarm_speed
        print(swarm_speed)
        self.swarm_speed_rad = swarm_speed/hive_radius
        self.sample_rate = sample_rate

        # Now initialise position
        #
        # Perhaps the simplest way is to give the swarm position as angle
        # from some reference point
        self.swarm_position = 0

    def sample_swarm_positions(self, n_samples):
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
        hive_no = np.random.randint(self.n_hives)
        self.swarm_position = np.pi/12 + np.pi*hive_no/6

        total_samples = n_samples
        s_counter = 0       # Sample counter
        positions = np.empty((total_samples, 2))

        increment = self.swarm_speed_rad/self.sample_rate
        tolerance = increment

        while s_counter < total_samples:
            # Allocate positions while hive is stationary
            t_stay = linger_options[np.random.randint(len(linger_options))]
            sample_num = t_stay * self.sample_rate
            new_s_counter = s_counter + sample_num

            current_position = np.array(
                [[self.hive_radius * np.cos(self.swarm_position),
                  self.hive_radius * np.sin(self.swarm_position)]])

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
                    np.array([[self.hive_radius * np.cos(self.swarm_position),
                    self.hive_radius * np.sin(self.swarm_position)]]))

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

    def sample_swarm_volumes(self, n_samples):
        swarm_positions = self.sample_swarm_positions(n_samples)
        # print(swarm_positions)
        # print("Position: {}".format(swarm_positions[0]), end=", ")
        return hive_volumes(self.hives, swarm_positions)

class SwarmBuffer:
    """
    Wraps Swarm and generates samples for a large sequence. These are then
    returned chunk by chunk through sample_swarm_volumes.
    """

    def __init__(self, *args, **kwargs):
        self.swarm = Swarm(*args, **kwargs)

        # Generate volumes for 10 mins
        self.volumes = self.swarm.sample_swarm_volumes(41000 * 60 * 1)


        self.next_sample = 0

    def sample_swarm_volumes(self, n_samples):
        end_sample = self.next_sample + n_samples
        samples = np.take(
            self.volumes,
            range(self.next_sample, end_sample),
            mode='wrap',
            axis = 0)
        self.next_sample = end_sample % self.volumes.shape[0]

        return samples



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
    return rbf_kernel(swarm_positions, hives, gamma=1)
