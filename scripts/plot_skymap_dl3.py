from argparse import ArgumentParser

from astropy import units as u
from gammapy.maps import WcsNDMap
from matplotlib import pyplot as plt

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

    ax.legend()

    fig.savefig(output_path)


if __name__ == "__main__":
    main(**vars(args))
