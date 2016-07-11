from nose.tools import assert_equal, assert_true
import sys
from humanhive import swarm, hive
import numpy as np

def test_swarm():
    # Initialise a Swarm object
    # Just want to check I understand what's happening when I create an object

    n_hives = 6
    hive_radius = 3. # hive radius in m
    swarm_speed = 3. # m/s
    swarm_speed_rad = swarm_speed/hive_radius # rad/s

    hives = hive.generate_hive_circle(n_hives, hive_radius)

    test_swarm = swarm.Swarm(hive_radius, hives, swarm_speed, 441000)

    # Run some tests to check it gives the right results.

    test_positions = test_swarm.sample_swarm_positions(100)

    assert_equal(test_positions.shape, (100, 2))

#    print test_swarm.swarm_position

#    print "The swarm position is now at %f" % test_swarm.swarm_position
#    print "That corresponds to hive number %i" \
#           % int(6*(test_swarm.swarm_position-np.pi/12)/np.pi)

#    print test_positions

def test_hive_volumes():

    positions = np.random.rand(100, 2)
    hives = np.random.rand(6, 2)

    volumes = swarm.hive_volumes(hives, positions, sigma=0.1)
    assert_equal(volumes.shape, (6, 100))
    assert_true(np.all(volumes >= 0) and np.all(volumes <= 1))
