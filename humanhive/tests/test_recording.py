import os
from humanhive import humanhive as hh, samplestream


onesecond_file = os.path.join(
    os.path.dirname(__file__), "audio", "recorded_buzz.wav")


def test_recording():
    audio_data = samplestream.load_wave_file(
        onesecond_file, mono=True)

    print(audio_data.dtype)
    recording = hh.Recording(None)

    n_frames_per_chunk = 1024

    while len(audio_data) > 0:
        n_frames_to_take = min((len(audio_data), n_frames_per_chunk))
        recording.process_audio(
            audio_data[:n_frames_to_take], n_frames_per_chunk)
        audio_data = audio_data[n_frames_to_take:]
