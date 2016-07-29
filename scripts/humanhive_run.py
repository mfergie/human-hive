"""
The Human Hive
"""

import sys
import time
import argparse

import numpy as np
import pyaudio
from humanhive import samplestream, utils, sources
from humanhive import HumanHive

def build_parser():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument(
        "--n-channels",
        required=True,
        help="The number of channels to use for operation.",
        type=int)

    parser.add_argument(
        "--swarm-sample",
        required=True,
        help="Audio file containing swarm sample")

    parser.add_argument(
        "--device-id",
        help="The ID for the sound card to use.",
        default=0,
        type=int)

    parser.add_argument(
        "--recorded-samples-dir",
        required=False,
        help=(
            "Directory for saving recordings. "
            "Will be created if it doesn't exist."))

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()

    sample_rate = utils.get_sample_rate_for_device(args.device_id)

    print("Initialising...")
    humanhive = HumanHive(
        n_channels=args.n_channels,
        device_id=args.device_id,
        sample_rate=sample_rate,
        master_volume=0.2)


    audio_data = samplestream.load_wave_file(
        args.swarm_sample, mono=True)
    # Add a source
    humanhive.source_bank.add_source(
        sources.SwarmSource(
            audio_data,
            n_channels=args.n_channels,
            sample_rate=sample_rate))


    print("Starting audio stream")
    humanhive.start_stream()

    while humanhive.is_active():
        # print("is active")
        humanhive.run()
        # time.sleep(0.1)

    print("Closing audio stream")
    humanhive.close_stream()
