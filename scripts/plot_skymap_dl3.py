from argparse import ArgumentParser

import numpy as np
from astropy import units as u
from gammapy.maps import WcsNDMap
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output-path", required=True)
parser.add_argument(
    "--width",
    help="Width of skymap",
    default="4 deg",
    type=u.Quantity,
)
parser.add_argument("--n-bins", default=100)
args = parser.parse_args()


@u.quantity_input(width=u.deg)
def main(input_path, output_path, width, n_bins):
    skymap = WcsNDMap.read(input_path)

    geom = skymap.geom
    source = geom.center_skydir

    edges = u.Quantity(
        [
            u.Quantity(geom.pix_to_coord([i, j]))
            for i, j in zip(range(int(geom.npix[0])), range(int(geom.npix[1])))
        ],
    ).T

    patches = PatchCollection(
        [
            Circle(
                (source.ra.to_value(u.deg), source.dec.to_value(u.deg)),
                radius=0.3,
                color="k",
                ec="k",
                fc="#0000",
                fill=False,
            ),
        ]
        + [
            Circle(
                (
                    source.ra.to_value(u.deg) + 0.8 * np.sin(phi),
                    source.dec.to_value(u.deg) + 0.8 * np.cos(phi),
                ),
                radius=0.3,
                color="w",
                ec="w",
                fc="#0000",
                fill=False,
            )
            for phi in np.linspace(0, 2 * np.pi, 7)
        ],
        match_original=True,
    )

    fig, ax = plt.subplots()

    mesh = ax.pcolormesh(
        *edges.to_value(u.deg),
        skymap.data[0, ...],
        rasterized=True,
    )

    fig.colorbar(mesh, ax=ax)

    ax.set_xlabel("RA / deg")
    ax.set_ylabel("Dec / deg")
    ax.set_aspect(1)

    ax.scatter(
        source.ra.to_value(u.deg),
        source.dec.to_value(u.deg),
        color="w",
        edgecolor="k",
        label="Source",
    )

    ax.add_collection(patches)

    ax.legend()

    fig.savefig(output_path)


if __name__ == "__main__":
    main(**vars(args))
