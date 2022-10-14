from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()

from astropy import units as u
from astropy.table import Table
from matplotlib import pyplot as plt

energy_unit = u.TeV


def main(input_path, output):
    gh_cuts = Table.read(input_path, hdu="GH_CUTS")

    fig, ax = plt.subplots()

    ax.errorbar(
        gh_cuts["center"].quantity.to_value(energy_unit),
        gh_cuts["cut"],
        xerr=(gh_cuts["center"] - gh_cuts["low"], gh_cuts["high"] - gh_cuts["center"]),
        ls="",
        label="G/H Cut",
        # lw=2,
        color="black",
    )
    ax.set_xlabel(f"$E_{{reco}} / {energy_unit}$")
    ax.set_ylabel("Gammaness")

    ax.bar(
        gh_cuts["center"].quantity.to_value(energy_unit),
        -(1 - gh_cuts["cut"]),
        bottom=1,
        width=gh_cuts["high"] - gh_cuts["low"],
        color="gray",
        alpha=0.1,
        label="Selected Events",
    )

    ax.legend()

    ax.set_ylim(0, 1)

    ax.set_xscale("log")

    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
