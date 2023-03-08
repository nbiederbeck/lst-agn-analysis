from argparse import ArgumentParser

from astropy import units as u
from gammapy.irf import load_irf_dict_from_file
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()

energy_unit = u.TeV


def main(input_path, output):
    edisp = load_irf_dict_from_file(input_path)["edisp"]

    fig, ax = plt.subplots()

    im = ax.pcolormesh(
        edisp.axes["energy_true"].edges.to_value(energy_unit),
        edisp.axes["migra"].edges,
        edisp.data[..., 0].T,
        cmap="binary",
    )
    ax.set_xlabel(rf"$E_{{true}}$ / {energy_unit}")
    ax.set_ylabel(r"Migration Ratio $\mu$")
    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.axhline(1, color="C1", linestyle="dashed")

    ax.set_ylim(0.1, 10)

    fig.colorbar(im, ax=ax, label="Density (?)")

    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
