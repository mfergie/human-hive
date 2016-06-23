"""
The Human Hive
"""

import sys
import time
import argparse

import numpy as np
import pyaudio
from humanhive import samplestream
from humanhive import HumanHive

def build_parser():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument(
        "--n-channels",
        required=True,
        help="The number of channels to use for operation.",
        type=int)

    parser.add_argument(
        "--swarm-samples-dir",
        required=True,
        help="Directory containing audio files of swarm samples")

    parser.add_argument(
        "--recording-samples-dir",
        required=False,
        help=(
            "Directory for saving recordings. "
            "Will be created if it doesn't exist."))

    return parser


if __name__ == "__main__":
    assert False, "Unfinished"

    humanhive = HumanHive(**args)
    humanhive.run()
