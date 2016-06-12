from nose.tools import assert_equal
import os

from humanhive import samplestream

onesecond_file = os.path.join(
    os.path.dirname(__file__), "audio", "onesecond.wav")

def test_load_wave_file():

    audio = samplestream.load_wave_file(onesecond_file)

    assert_equal(audio.shape, (44100, 2))
