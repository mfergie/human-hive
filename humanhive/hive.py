"""
The Human Hive
"""
import numpy as np

def generate_hive_circle(n_hives, hive_radius):
    """
    Space the hives evenly around a circle. 0 angle is the top bar hive
    """
    hives = []

    for i in range(n_hives):
        theta = np.pi/12 + i*np.pi/6
        hives.append([hive_radius * np.cos(theta), hive_radius * np.sin(theta)])

    return hives
