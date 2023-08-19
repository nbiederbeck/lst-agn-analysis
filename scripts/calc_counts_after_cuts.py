import json
from argparse import ArgumentParser

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import QTable
from lstchain.high_level.hdu_table import add_icrs_position_params
from lstchain.io import read_data_dl2_to_QTable
from lstchain.reco.utils import get_effective_time

parser = ArgumentParser()
parser.add_argument("--input-dl2", required=True)
parser.add_argument("--input-irf", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-c", "--config", required=True)
args = parser.parse_args()


def main(input_dl2, input_irf, config, output):
    with open(config, "r") as f:
        config = json.load(f)

    events = read_data_dl2_to_QTable(input_dl2, "on")
    mask = events['event_type'] == 32
    events = events[mask]

    t_eff, t_ela = get_effective_time(events)
    events.meta["t_effective"] = t_eff
    events.meta["t_elapsed"] = t_ela

    source = SkyCoord(
        ra=config["DataReductionFITSWriter"]["source_ra"],
        dec=config["DataReductionFITSWriter"]["source_dec"],
    )
    # adds "RA", "Dec", "theta" to events
    events = add_icrs_position_params(events, source)

    columns = ["gh_score", "reco_energy", "RA", "Dec", "theta"]
    events = events[columns]

    gh_cuts = QTable.read(input_irf, hdu="GH_CUTS")

    events["gh_bin"] = np.digitize(
        events["reco_energy"],
        gh_cuts["high"],
    )
    events["gh_cut"] = gh_cuts["cut"][events["gh_bin"]]
    gh_mask = events["gh_score"] >= events["gh_cut"]
    events["gh_mask"] = gh_mask

    rad_max_cuts = QTable.read(input_irf, hdu="RAD_MAX")

    events["theta_bin"] = np.digitize(
        events["reco_energy"],
        rad_max_cuts["ENERG_HI"][0],
    )
    events["theta_cut"] = rad_max_cuts["RAD_MAX"][0, 0][events["theta_bin"]]
    theta_mask = events["theta"] <= events["theta_cut"]
    events["theta_mask"] = theta_mask

    table = QTable(
        {
            "after_trigger": [
                len(events[events["gh_bin"] == i]) for i in range(len(gh_cuts))
            ],
            "after_gh": [
                len(events[(events["gh_bin"] == i) & gh_mask])
                for i in range(len(gh_cuts))
            ],
            "after_gh_theta": [
                len(events[(events["gh_bin"] == i) & gh_mask & theta_mask])
                for i in range(len(gh_cuts))
            ],
            "rad_max_cut": rad_max_cuts["RAD_MAX"][0, 0],
            **gh_cuts,
        },
        meta={"t_elapsed": t_ela, "t_effective": t_eff},
    )
    table.write(output, path="cuts", overwrite=True, serialize_meta=True)


if __name__ == "__main__":
    main(**vars(args))
