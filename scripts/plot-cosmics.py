from argparse import ArgumentParser

from astropy.table import Table
from astropy.time import Time
from config import Config
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("-o", "--output_path", required=True)
parser.add_argument("-c", "--config", required=True)
args = parser.parse_args()

config = Config.parse_file(args.config)


def main():
    runsummary = Table.read(args.input_path)
    runsummary = runsummary[runsummary["mask_run_selection"]]
    time = Time(runsummary["time"], format="unix", scale="utc")
    fig, ax = plt.subplots()

    cosmics_rate = runsummary["cosmics_rate"]

    ax.plot(
        time.datetime,
        cosmics_rate,
        ".",
    )
    ax.set_xlim(ax.get_xlim())
    ax.fill_between(
        ax.get_xlim(),
        [config.cosmics.ll],
        [config.cosmics.ul],
        alpha=0.1,
        label="Selection",
    )

    ax.set_xlabel("Time")
    ax.set_ylabel("Rate / 1/s")
    ax.tick_params(axis="x", rotation=30)

    ax.legend()

    fig.savefig(args.output_path)


if __name__ == "__main__":
    main()
