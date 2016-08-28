#!/usr/bin/env python3
"""
The Human Hive
"""

import sys
import time
import argparse
import multiprocessing

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
        "--output-device-id",
        help="The ID for the output sound card to use.",
        default=None,
        # type=int
    )

    parser.add_argument(
        "--input-device-id",
        help="The ID for the input sound card to use.",
        default=None,
        # type=int
    )

    parser.add_argument(
        "--occasional-sample",
        required=False,
        help=("An audio file to a play occasionally through a random hive")
    )

    parser.add_argument(
        "--recorded-samples-dir",
        required=False,
        help=(
            "Directory for saving recordings. "
            "Will be created if it doesn't exist."))

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()

    sample_rate = 48000#utils.get_sample_rate_for_device(args.output_device_id)

    print("Initialising...")
    humanhive = HumanHive(
        n_channels=args.n_channels,
        output_device_id=args.output_device_id,
        input_device_id=args.input_device_id,
        sample_rate=sample_rate,
        master_volume=1.0)


    audio_data = samplestream.load_wave_file(
        args.swarm_sample, mono=True)
    # Add a source
    humanhive.source_bank.add_source(
        sources.SwarmSource(
            audio_data,
            n_channels=args.n_channels,
            sample_rate=sample_rate))

    if args.occasional_sample:
        occ_audio_data = samplestream.load_wave_file(
            args.occasional_sample, mono=True)
        # Add a source
        humanhive.source_bank.add_source(
            sources.OccasionalSource(
                occ_audio_data,
                n_channels=args.n_channels,
                sample_rate=sample_rate,
                repeat_period=10*60,
                volume=1.0))


    print("Entering HumanHive main loop")
    humanhive.run()

    print("Exiting")
