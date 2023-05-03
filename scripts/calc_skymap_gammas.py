import json
from argparse import ArgumentParser

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from gammapy.data import DataStore
from gammapy.maps import MapAxis, WcsGeom, WcsNDMap

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output-path", required=True)
parser.add_argument("-c", "--config", required=True)
parser.add_argument("--obs-id", required=True)
parser.add_argument(
    "--width",
    help="Width of skymap",
    default="3 deg",
    type=u.Quantity,
)
parser.add_argument("--n-bins", default=100)
args = parser.parse_args()


@u.quantity_input(width=u.deg)
def main(input_path, config, output_path, obs_id, width, n_bins):  # noqa: PLR0913
    with open(config, "r") as f:
        config = json.load(f)

    ds = DataStore.from_dir(input_path)

    obs = ds.obs(int(obs_id), ["aeff"])

    events = obs.events

    evts = events.radec

    source = SkyCoord(
        config["DataReductionFITSWriter"]["source_ra"],
        config["DataReductionFITSWriter"]["source_dec"],
        frame="icrs",
    )

    r = width / 2
    bins = u.Quantity(
        [
            np.linspace(source.ra - r, source.ra + r, n_bins + 1),
            np.linspace(source.dec - r, source.dec + r, n_bins + 1),
        ],
    )

    hist, *edges = np.histogram2d(
        evts.ra.to_value(u.deg),
        evts.dec.to_value(u.deg),
        bins.to_value(u.deg),
    )

    energy_axis = MapAxis.from_edges(
        u.Quantity([1e-5, 1e5], u.TeV),  # basically [-inf, inf], but finite
        name="energy",
    )
    geom = WcsGeom.create(
        (n_bins, n_bins),
        skydir=source,
        binsz=width / n_bins,
        width=width,
        axes=[energy_axis],
    )

    skymap = WcsNDMap(geom, hist)

    skymap.write(output_path, overwrite=True)

    # patches = PatchCollection(
    #     [
    #         Circle(
    #             (source.ra.to_value(u.deg), source.dec.to_value(u.deg)),
    #             radius=0.3,
    #             color="k",
    #             ec="k",
    #             fc="#0000",
    #             fill=False,
    #         ),
    #     ]
    #     + [
    #         Circle(
    #             (
    #                 source.ra.to_value(u.deg) + 0.8 * np.sin(phi),
    #                 source.dec.to_value(u.deg) + 0.8 * np.cos(phi),
    #             ),
    #             radius=0.3,
    #             color="w",
    #             ec="w",
    #             fc="#0000",
    #             fill=False,
    #         )
    #         for phi in np.linspace(0, 2 * np.pi, 7)
    #     ],
    #     match_original=True,
    # )

    # fig, ax = plt.subplots()

    # ax.pcolormesh(*edges, hist)

    # ax.set_xlabel("RA / deg")
    # ax.set_ylabel("Dec / deg")
    # ax.set_aspect(1)

    # ax.scatter(
    #     source.ra.to_value(u.deg),
    #     source.dec.to_value(u.deg),
    #     color="w",
    #     edgecolor="k",
    #     label="Source",
    # )

    # ax.add_collection(patches)

    # ax.legend()

    # fig.savefig(output_path)


if __name__ == "__main__":
    main(**vars(args))
