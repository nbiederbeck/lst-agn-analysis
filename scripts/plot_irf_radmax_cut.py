from argparse import ArgumentParser

import numpy as np
from astropy import units as u
from astropy.table import Table
from gammapy.maps import MapAxis
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(input_path, output):
    rad_max = Table.read(input_path, hdu="RAD_MAX")
    energy_unit = u.TeV
    angle_unit = u.deg

    energy_edges = np.unique(
        np.concatenate(
            [
                rad_max["ENERG_LO"].quantity.to_value(energy_unit).flatten(),
                rad_max["ENERG_HI"].quantity.to_value(energy_unit).flatten(),
            ],
        ),
    )
    energy_axis = MapAxis.from_energy_edges(energy_edges, unit=energy_unit)
    rmax = rad_max["RAD_MAX"].quantity.to_value(angle_unit).flatten()

    fig, ax = plt.subplots()

    ax.errorbar(
        energy_axis.center,
        rmax,
        xerr=(
            energy_axis.center - energy_axis.edges_min,
            energy_axis.edges_max - energy_axis.center,
        ),
        ls="",
        color="black",
        label="Rad Max",
    )

    # ax.bar(
    #     energy_axis.center,
    #     rmax,
    #     width=energy_axis.edges_max - energy_axis.edges_min,
    #     color="gray",
    #     alpha=0.1,
    #     label="Selected Events",
    # )

    ax.set_ylim(0, 0.5)

    ax.set_xscale("log")
    ax.set_xlabel(f"$E_{{\\mathrm{{reco}}}}$ / {energy_unit}")
    ax.set_ylabel(f"$\theta$ / {angle_unit}")

    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
