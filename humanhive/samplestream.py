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
    samples: array_like, shape: (n_channels, n_samples)
        Returns the audio samples
    """

    with wave.open(filename, 'rb') as wavefile:

        if (ensure_sample_rate is not None and
                wavefile.getframerate() != ensure_sample_rate):
            raise ValueError("Sample rate of audio {} doesn't match {}".format(
                wavefile.getframerate(), ensure_sample_rate))

        n_channels = wavefile.getnchannels()
        n_samples = wavefile.getnframes()

        samples = np.frombuffer()
        samples = np.ndarray(n_channels, n_samples, dtype=np.float32)
        samples

class SampleStream():
    """
    Provides access to an audio buffer chunk by chunk.
    """

    def __init__(self, audio_buffer):

        if audio_buffer.ndim != 1:
            raise ValueError("Only mono audio supported")

        self.audio_buffer = audio_buffer
        self.next_sample = 0

    def retrieve_samples(n_samples):
        end_sample = self.next_sample + n_samples
        samples = np.take(
            self.audio_buffer,
            range(self.next_sample, end_sample),
            mode='wrap')
        self.next_sample = end_sample % self.audio_buffer.size

        return samples
