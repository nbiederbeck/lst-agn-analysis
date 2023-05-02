from argparse import ArgumentParser

import numpy as np
from astropy import units as u
from astropy.table import Table
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("-i", "--input-paths", required=True, nargs="+")
parser.add_argument("-o", "--output-path", required=True)
parser.add_argument("--norm", default="none")
args = parser.parse_args()


def main(input_paths, output_path, norm):
    cuts_after_trigger = []
    cuts_after_gh = []
    cuts_after_gh_theta = []
    t_effective = []
    t_elapsed = []

    for path in input_paths:
        cuts = Table.read(path, path="cuts")
        cuts_after_trigger.append(cuts["after_trigger"])
        cuts_after_gh.append(cuts["after_gh"])
        cuts_after_gh_theta.append(cuts["after_gh_theta"])
        t_effective.append(cuts.meta["t_effective"])
        t_elapsed.append(cuts.meta["t_elapsed"])

    fig, ax = plt.subplots()

    x = cuts["center"]
    xerr = (cuts["high"] - x, x - cuts["low"])

    t_eff = u.Quantity(t_effective).reshape(-1, 1)
    if norm == "none":
        norm = u.Quantity(1)
    elif norm == "eff":
        norm = np.sum(t_eff)
    else:
        raise ValueError(f"Unsupported norm {norm}")

    cuts_after_trigger = np.sum(
        np.array(cuts_after_trigger) * t_eff.to_value("s") / norm,
        axis=0,
    )
    cuts_after_gh = np.sum(
        np.array(cuts_after_gh) * t_eff.to_value("s") / norm,
        axis=0,
    )
    cuts_after_gh_theta = np.sum(
        np.array(cuts_after_gh_theta) * t_eff.to_value("s") / norm,
        axis=0,
    )

    ax.errorbar(
        x,
        cuts_after_trigger,
        xerr=xerr,
        ls="",
        label="Trigger",
    )
    ax.errorbar(
        x,
        cuts_after_gh,
        xerr=xerr,
        ls="",
        label="GH Cut",
    )
    ax.errorbar(
        x,
        cuts_after_gh_theta,
        xerr=xerr,
        ls="",
        label="Theta Cut",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel(x.unit)
    ax.set_ylabel(cuts_after_trigger.unit)

    ax.legend(title="Counts after")

    fig.savefig(output_path)


if __name__ == "__main__":
    main(**vars(args))
