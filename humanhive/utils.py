import numpy as np

### Work around for librosa importing matplotlib
import mock
import sys
sys.modules.update((mod_name, mock.Mock()) for mod_name in ['matplotlib', 'matplotlib.pyplot', 'matplotlib.image'])

import librosa.feature
import librosa.core

import pyaudio


def compute_audio_volume_per_frame(in_data):
    rmse = librosa.feature.rmse(in_data)
    return rmse

def compute_audio_volume(in_data):
    return np.mean(compute_audio_volume_per_frame(in_data))

def compute_audio_threshold_crossings(frame_volumes, threshold):
    """
    Finds the sample indices where the volume passes above and below the
    volume threshold.
    """
    thresh_centre = frame_volumes - threshold

    crossings_up = np.nonzero(
        (thresh_centre[:-1] < 0) and (thresh_centre[1:] >= 0))[0]
    crossings_down = np.nonzero(
        (thresh_centre[:-1] >= 0) and (thresh_centre[1:] < 0))[0]

    return crossings_up, crossings_down


def get_sample_rate_for_device(device_id=0):
    """
    Get's the default sample rate for the audio device.
    """
    p = pyaudio.PyAudio()

    device_params = p.get_device_info_by_index(device_id)

    sample_rate = int(device_params["defaultSampleRate"])

    return sample_rate
