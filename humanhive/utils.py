import numpy as np
import librosa.feature
import librosa.core

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
