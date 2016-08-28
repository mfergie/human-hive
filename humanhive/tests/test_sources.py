import os
from nose.tools import assert_true
import numpy as np
from humanhive import samplestream, sources

onesecond_file = os.path.join(
    os.path.dirname(__file__), "audio", "onesecond.wav")

def test_occasional_source():


    audio_data = samplestream.load_wave_file(onesecond_file, mono=True)

    print("audio_data shape: {}".format(audio_data.shape))

    source = sources.OccasionalSource(
        audio_data,
        2,
        44100,
        repeat_period=1)

    for n in range(441):
        frames = source.get_frames(100)
        assert_true(np.abs(frames).max() == 0)

    for n in range(441):
        frames = source.get_frames(100)
        assert_true(np.abs(frames).max() > 0)

    for n in range(441):
        frames = source.get_frames(100)
        assert_true(np.abs(frames).max() == 0)
