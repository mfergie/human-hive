from nose.tools import assert_equal
import os

from humanhive import samplestream
from numpy.testing import assert_array_equal

onesecond_file = os.path.join(
    os.path.dirname(__file__), "audio", "onesecond.wav")

def test_load_wave_file():

    audio = samplestream.load_wave_file(onesecond_file)

    assert_equal(audio.shape, (44100, 2))


def test_sample_stream_mono():

    # Load one second file

    audio = samplestream.load_wave_file(onesecond_file)
    assert_equal(audio.shape, (44100, 2))

    sample_stream = samplestream.SampleStream(audio[:,0])

    # Request all samples at once
    samples = sample_stream.retrieve_samples(44100)
    assert_equal(samples.shape, (44100,))

    # Request samples 100 at a time.
    first_batch = sample_stream.retrieve_samples(100)
    for n in range(1, 44100//100):
        audio = sample_stream.retrieve_samples(100)
        print(audio)
    last_batch = sample_stream.retrieve_samples(100)

    assert_array_equal(first_batch, last_batch)
