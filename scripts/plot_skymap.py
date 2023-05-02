#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser

import numpy as np
from gammapy.maps import WcsMap
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("-i", "--input-paths", required=True, nargs="+")
parser.add_argument("-o", "--output-path", required=True)
args = parser.parse_args()


def main(input_paths, output_path):
    data = []
    for path in input_paths:
        skymap = WcsMap.read(path, map_type="wcs")
        data.append(skymap.data)

    fig, ax = plt.subplots()

    ax.imshow(np.sum(data, axis=0)[0])

    ax.scatter(
        *skymap.geom.coord_to_pix(skymap.geom.center_coord)[:-1],
        marker="*",
    )

    fig.savefig(output_path)


if __name__ == "__main__":
    main(**vars(args))
