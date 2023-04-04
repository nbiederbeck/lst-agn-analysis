from argparse import ArgumentParser

from gammapy.estimators import FluxPoints
from matplotlib import pyplot as plt
from matplotlib.dates import ConciseDateFormatter

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(input_path, output):
    lc = FluxPoints.read(input_path, format="lightcurve")

    fig, ax = plt.subplots()
    lc.plot(ax=ax)
    ax.set_ylabel(
        r"$\Phi \:\:/\:\: "
        + r"\si{\per\centi\meter\squared\per\second\per\tera\electronvolt}$",
    )
    ax.set_xlabel("Date")
    ax.xaxis.set_major_formatter(ConciseDateFormatter(ax.xaxis.get_major_locator()))
    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
