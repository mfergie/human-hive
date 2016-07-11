import numpy as np
from nose.tools import assert_equal, assert_true

from humanhive import utils

def test_compute_audio_volume_per_frame():
    # Compute volume of sin wave at max amplitude.

    N = 1024
    sin_data = np.sin(np.linspace(0, 20*np.pi, N))
    volumes = utils.compute_audio_volume_per_frame(sin_data)
    print(volumes)
    assert_equal(volumes.shape, (N,))
    assert_true(np.allclose(volumes, 1))



def test_compute_audio_threshold_crossings():
    pass
