import nose
import sys
from humanhive import swarm
import numpy as np

def test_swarm():
    # Initialise a Swarm object
    # Just want to check I understand what's happening when I create an object

    r = 3. # hive radius in m
    swarm_speed = 3. # m/s
    swarm_speed_rad = swarm_speed/r # rad/s

    # Space the hives evenly around a circle. 0 angle is the top bar hive
    hives = []

    for i in range(0,6):
        theta = np.pi/12 + i*np.pi/6
        hives.append([r*np.cos(theta),r*np.sin(theta)])

    test_swarm = swarm.Swarm(r, hives, swarm_speed, 441000)

    # Run some tests to check it gives the right results.

    test_positions = test_swarm.sample_swarm_positions_rand(100)

#    print test_swarm.swarm_position

#    print "The swarm position is now at %f" % test_swarm.swarm_position
#    print "That corresponds to hive number %i" \
#           % int(6*(test_swarm.swarm_position-np.pi/12)/np.pi)

#    print test_positions
