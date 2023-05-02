#!/usr/bin/env python
# coding: utf-8

import json
from argparse import ArgumentParser

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from gammapy.maps import MapAxis, WcsGeom, WcsNDMap
from lstchain.high_level.hdu_table import add_icrs_position_params
from lstchain.io import read_data_dl2_to_QTable
from lstchain.reco.utils import get_effective_time

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output-path", required=True)
parser.add_argument("-c", "--config", required=True)
args = parser.parse_args()


def main(input_path, output_path, config):
    with open(config, "r") as f:
        config = json.load(f)

    events = read_data_dl2_to_QTable(input_path, "on")

    t_eff, t_ela = get_effective_time(events)
    events.meta["t_effective"] = t_eff
    events.meta["t_elapsed"] = t_ela

    source = SkyCoord(
        ra=config["DataReductionFITSWriter"]["source_ra"],
        dec=config["DataReductionFITSWriter"]["source_dec"],
    )
    # adds "RA", "Dec", "theta" to events
    events = add_icrs_position_params(events, source)

    evts = SkyCoord(events["RA"], events["Dec"], frame="icrs")

    d = u.Quantity(4, u.deg)
    n_bins = 100
    bins = u.Quantity(
        [
            np.linspace(source.ra - d, source.ra + d, n_bins + 1),
            np.linspace(source.dec - d, source.dec + d, n_bins + 1),
        ],
    )

    hist, *edges = np.histogram2d(
        evts.ra.to_value(u.deg),
        evts.dec.to_value(u.deg),
        bins=bins.to_value(u.deg),
    )

    energy_axis = MapAxis.from_edges(
        u.Quantity([1e-5, 1e5], u.TeV),
        name="energy",
    )
    geom = WcsGeom.create(
        (n_bins, n_bins),
        skydir=source,
        binsz=2 * d / n_bins,
        width=2 * d,
        axes=[energy_axis],
    )

    skymap = WcsNDMap(geom, hist)

    skymap.write(output_path, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
