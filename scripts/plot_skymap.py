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

    geom = skymap.geom
    center = geom.center_coord
    source = geom.center_skydir

    fig, ax = plt.subplots()

    ax.imshow(np.sum(data, axis=0)[0])

    ax.scatter(
        *geom.coord_to_pix(center)[:-1],
        marker="*",
    )

    ax.set_xticks(
        geom.coord_to_pix(center)[0],
        labels=[f"{source.ra.to_value(angle):.2f}"],
    )
    ax.set_yticks(
        geom.coord_to_pix(center)[1],
        labels=[f"{source.dec.to_value(angle):.2f}"],
    )

    ax.set_xlabel(f"RA / {angle}")
    ax.set_ylabel(f"Dec / {angle}")

    fig.savefig(output_path)


if __name__ == "__main__":
    main(**vars(args))
