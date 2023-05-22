from argparse import ArgumentParser

from astropy.table import Table
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output-path", required=True)
args = parser.parse_args()


def main(input_path, output_path):
    cuts = Table.read(input_path, path="cuts")

    x = cuts["center"]
    xerr = (cuts["high"] - x, x - cuts["low"])

    fig, ax = plt.subplots()

    ax.errorbar(
        x,
        cuts["after_trigger"],
        xerr=xerr,
        ls="",
        label="Trigger",
    )
    ax.errorbar(
        x,
        cuts["after_gh"],
        xerr=xerr,
        ls="",
        label="GH Cut",
    )
    ax.errorbar(
        x,
        cuts["after_gh_theta"],
        xerr=xerr,
        ls="",
        label="Theta Cut",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel(rf"E_{{\text{{reco}}}} \:/\: {x.unit}")
    ax.set_ylabel(cuts["after_trigger"].unit)

    ax.legend(title="Counts after")

    fig.savefig(output_path)


if __name__ == "__main__":
    main(**vars(args))
