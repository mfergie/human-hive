"""
samplestream module

Functionality for loading audio samples and looping them in a stream-friendly
manner.
"""
import os
import wave
import numpy as np

def load_wave_file(filename, ensure_sample_rate=None, mono=False):
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

    wavefile = wave.open(filename, 'rb')

    if (ensure_sample_rate is not None and
            wavefile.getframerate() != ensure_sample_rate):
        raise ValueError("Sample rate of audio {} doesn't match {}".format(
            wavefile.getframerate(), ensure_sample_rate))
    if wavefile.getsampwidth() != 2:
        raise ValueError("Only supports WAV files with sample width of 2")

    n_channels = wavefile.getnchannels()
    n_samples = wavefile.getnframes()
    # print("n_channels: {}, n_samples: {}".format(n_channels, n_samples))
    samples = np.frombuffer(
        wavefile.readframes(n_samples), dtype=np.int16)
    samples = samples.reshape(-1, n_channels)

    wavefile.close()

    if mono:
        # Only take first channel, and flatten
        samples = samples[:,0].flatten()

    return samples


def load_samples_from_dir(sample_dir, extensions=(".wav",)):
    files = os.listdir(sample_dir)
    wav_files = [fn for fn in files if os.path.splitext(fn)[1] in extensions]
    samples_list = [
        load_wave_file(os.path.join(sample_dir, fn), mono=True) for fn in wav_files]

    return samples_list


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
