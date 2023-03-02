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
    fig, (ax10, ax30) = plt.subplots(nrows=2, sharex=True)

    cosmics_rate = runsummary["num_cosmics"] / runsummary["elapsed_time"]
    cosmics_rate_above10 = cosmics_rate * runsummary["cosmics_fraction_pulses_above10"]
    cosmics_rate_above30 = cosmics_rate * runsummary["cosmics_fraction_pulses_above30"]

    ax10.plot(
        time.datetime,
        cosmics_rate_above10,
        ".",
        label=r"Pulses $>$ 10 p.e.",
    )
    ax30.plot(
        time.datetime,
        cosmics_rate_above30,
        ".",
        label=r"Pulses $>$ 30 p.e.",
    )

    ax10.set_xlim(ax10.get_xlim())
    ax10.fill_between(
        ax10.get_xlim(),
        config.cosmics_10_ll,
        config.cosmics_10_ul,
        alpha=0.1,
        label="Selection",
    )

    ax30.set_xlim(ax30.get_xlim())
    ax30.fill_between(
        ax30.get_xlim(),
        config.cosmics_30_ll,
        config.cosmics_30_ul,
        alpha=0.1,
        label="Selection",
    )

    ax10.legend()
    ax30.legend()

    ax30.set_xlabel("Time")

    ax10.set_ylabel("Rate / 1/s")
    ax30.set_ylabel("Rate / 1/s")

    ax30.tick_params(axis="x", rotation=30)

    fig.savefig(args.output_path)


if __name__ == "__main__":
    main()
