#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser

import numpy as np
from astropy import units as u
from gammapy.maps import WcsMap
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("-i", "--input-paths", required=True, nargs="+")
parser.add_argument("-o", "--output-path", required=True)
args = parser.parse_args()

angle = u.deg


def main(input_paths, output_path):
    data = []
    for path in input_paths:
        skymap = WcsMap.read(path, map_type="wcs")
        data.append(skymap.data)

    data = np.sum(data, axis=0)[0]

    geom = skymap.geom
    source = geom.center_skydir

    edges = u.Quantity(
        [
            u.Quantity(geom.pix_to_coord([i, j]))
            for i, j in zip(range(int(geom.npix[0])), range(int(geom.npix[1])))
        ],
    ).T

    fig, ax = plt.subplots()

    ax.pcolormesh(*edges.to_value(angle), data, rasterized=True)

    ax.scatter(
        source.ra.to_value(u.deg),
        source.dec.to_value(u.deg),
        ec="k",
        fc="w",
        label="Source",
    )

    ax.set_xlabel(f"RA / {angle}")
    ax.set_ylabel(f"Dec / {angle}")

    ax.legend()

    ax.set_aspect(1)

    fig.savefig(output_path)


if __name__ == "__main__":
    main(**vars(args))
