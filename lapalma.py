#!/usr/bin/env python3
from argparse import ArgumentParser
from subprocess import run

parser = ArgumentParser(
    description="Copy built data files from the cluster to locally create plots.",
)
parser.add_argument(
    "--hostname",
    help="The hostname as configured in you ~/.ssh/config, e.g. `cp01`.",
    required=True,
)
parser.add_argument(
    "--remote-path",
    help="Path to your directory on the cluster, "
    "e.g. `/fefs/aswg/workspace/<username>/lst-agn-analysis/build`. "
    "Can be absolute (start with `/`) otherwise it is relative to the home. "
    "Get the absoulte path of any directory with "
    "`realpath <directory>` on the cluster.",
    required=True,
)
parser.add_argument(
    "--exclude",
    help="Patterns to additionally exclude from copying. Comma separated string. "
    "When you use globs (`*`), remember to quote it in single quotes, "
    "e.g. `--exclude='*.pdf,*.png'`.",
    default=None,
    type=str,
)
parser.add_argument(
    "--rsync-args",
    help="Custom command line arguments for rsync. Check `man rsync` for info. "
    "Try `--rsync-args='-nv'` for a verbose dry-run.",
    default="",
    type=str,
)
args = parser.parse_args()

exclude_patterns = [
    "dl1_*.h5",
    "dl2_*.h5",
    "dl3_*.fits.gz",
    "*.log",
    "logs/*",
    "models/model*",
    "*.pdf",
]


def main():
    rsync = "rsync -auh --info=progress2 "
    rsync += args.rsync_args + " "
    for pat in exclude_patterns:
        rsync += f"--exclude='{pat}' "
    if args.exclude is not None:
        for pat in args.exclude.split(","):
            rsync += f"--exclude='{pat}' "
    cmd = f"{rsync} '{args.hostname}:{args.remote_path.rstrip('/')}' ."
    print(cmd)
    run(cmd, shell=True, capture_output=False, check=True)


if __name__ == "__main__":
    main()
