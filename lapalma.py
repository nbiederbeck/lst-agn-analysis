#!/usr/bin/env python3
from argparse import ArgumentParser
from subprocess import run

parser = ArgumentParser(
    description="Copy data files from the cluster to locally create plots.",
)
parser.add_argument(
    "--hostname",
    help="The hostname as configured in you ~/.ssh/config, e.g. `cp01`.",
    required=True,
)
parser.add_argument(
    "--remote-path",
    help="Path to your directory on the cluster, "
    "e.g. `/fefs/aswg/workspace/<username>/lst-agn-analysis/`. "
    "Can be absolute (start with `/`) otherwise it is relative to the home.",
    required=True,
)
args = parser.parse_args()

filelist = [
    "build/dl1-datachecks-masked.h5",
]
files = "{" + ",".join(filelist) + "}"


def main():
    rsync = "rsync -auh --info=progress2 --exclude-from=.gitignore"
    cmd = f"{rsync} '{args.hostname}:{args.remote_path}/{files}' ."
    run(cmd, shell=True, capture_output=True, check=True)


if __name__ == "__main__":
    main()
