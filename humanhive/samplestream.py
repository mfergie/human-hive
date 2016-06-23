"""
samplestream module

Functionality for loading audio samples and looping them in a stream-friendly
manner.
"""
import wave
import numpy as np

def load_wave_file(filename, ensure_sample_rate=None):
    """
    Load a WAV file.

    Parameters
    ----------
    filename: str
        Path to file to open
    ensure_sample_rate: int or None
        Ensure that the WAV matches the sample rate. If not, raises a
        ValueError

    Returns
    -------
    samples: array_like, shape: (n_samples, n_channels)
        Returns the audio samples
    """

    with wave.open(filename, 'rb') as wavefile:

        if (ensure_sample_rate is not None and
                wavefile.getframerate() != ensure_sample_rate):
            raise ValueError("Sample rate of audio {} doesn't match {}".format(
                wavefile.getframerate(), ensure_sample_rate))
        if wavefile.getsampwidth() != 2:
            raise ValueError("Only supports WAV files with sample width of 2")

        n_channels = wavefile.getnchannels()
        n_samples = wavefile.getnframes()
        print("n_channels: {}, n_samples: {}".format(n_channels, n_samples))
        samples = np.frombuffer(
            wavefile.readframes(n_samples), dtype=np.int16)
        samples = samples.reshape(-1, n_channels)

        return samples

def copy_n_channels(audio, n_channels):
    """
    Copy a mono audio feed as shape (n_samples,) into an n_channels audio feed
    of shape (N, n_channels)
    """
    assert audio.ndim == 1, "Error, audio must be single channel"
    return np.hstack([audio[:,np.newaxis] for _ in range(n_channels)])


class SampleStream():
    """
    Provides access to an audio buffer chunk by chunk.
    """

    def __init__(self, audio_buffer):

        if audio_buffer.ndim != 1:
            raise ValueError("Only mono audio supported")

        self.audio_buffer = audio_buffer
        self.next_sample = 0

    def retrieve_samples(self, n_samples):
        end_sample = self.next_sample + n_samples
        samples = np.take(
            self.audio_buffer,
            range(self.next_sample, end_sample),
            mode='wrap')
        self.next_sample = end_sample % self.audio_buffer.size

        return samples
