from argparse import ArgumentParser

import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.table import Table
from astropy.time import Time
from config import Config

parser = ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("datacheck_path")
parser.add_argument("--output-runlist", required=True)
parser.add_argument("--output-datachecks", required=True)
parser.add_argument("-c", "--config", required=True)
args = parser.parse_args()

config = Config.parse_file(args.config)


def get_mask(x, le=np.inf, ge=-np.inf):
    return np.logical_and(
        np.greater_equal(x, ge),
        np.less_equal(x, le),
    )


def nmad(x):
    """Normalized Median Absolute Difference.

    Similar to standard deviation, but more robust to outliers [0], [1].

    [0]: https://en.wikipedia.org/wiki/Robust_measures_of_scale
    [1]: https://en.wikipedia.org/wiki/Median_absolute_deviation

    """
    return 1.4826 * np.median(np.abs(x - np.median(x)))


def bounds_std(x, n_sig=1):
    m = np.mean(x)
    s = n_sig * np.std(x)

    return (m - s, m + s)


def bounds_mad(x, n_sig=1):
    m = np.median(x)
    s = n_sig * nmad(x)

    return (m - s, m + s)


if __name__ == "__main__":
    runs = pd.read_csv(args.input_path)

    run_ids = np.array(runs["Run ID"])

    runsummary = Table.read(args.datacheck_path)

    time = Time(runsummary["time"], format="unix", scale="utc")

    mask_time = get_mask(
        time,
        ge=Time("2020-12-12", scale="utc"),
        le=Time("2022-05-24", scale="utc"),
    )

    mask_run_id = np.in1d(np.array(runsummary["runnumber"]), run_ids)

    mask_pedestals_ok = np.isfinite(runsummary["num_pedestals"])

    # Exclude runs that are too far from source

    tel_pointing = SkyCoord(
        ra=runsummary["mean_ra"],
        dec=runsummary["mean_dec"],
    )

    source_coordinates = SkyCoord(
        ra=config.source_ra_deg,
        dec=config.source_dec_deg,
        unit=u.deg,
    )

    separation = tel_pointing.separation(source_coordinates)

    mask_separation_low = np.isclose(
        u.Quantity(0.4, u.deg), separation, rtol=0, atol=0.15
    )

    mask = mask_pedestals_ok & mask_run_id & mask_time & mask_separation_low

    runsummary["mask_run_id"] = mask_run_id
    runsummary["mask_time"] = mask_time
    runsummary["mask_separation_low"] = mask_separation_low
    runsummary["mask_pedestals_ok"] = mask_pedestals_ok

    runsummary["mask_run_selection"] = mask

    after_pedestals_run_id_time_separation = np.count_nonzero(mask)
    s = (
        "After selecting the time of the dataset used in AGN Zoo Paper, "
        "after removing runs with problems in pedestals and "
        "after selecting runs that are close to the observed target, "
        f"{after_pedestals_run_id_time_separation} runs are kept."
    )
    print(s)

    # Exclude runs with high zenith (?)
    #
    # Better later.

    location = EarthLocation.of_site("lapalma")

    altaz = AltAz(obstime=time[mask], location=location)

    ped_std = runsummary["ped_charge_stddev"]

    mask_pedestal_charge = get_mask(
        ped_std,
        ge=config.pedestal_ll,
        le=config.pedestal_ul,
    )

    runsummary["mask_pedestal_charge"] = mask_pedestal_charge & mask
    mask = runsummary["mask_pedestal_charge"] & mask

    after_pedestal_charge = np.count_nonzero(mask)
    s = (
        "After checking for the deviation of the pedestal charges, "
        "possibly dependent on the moon elevation and illumination, "
        f"{after_pedestal_charge} runs are kept."
    )
    print(s)

    # Check cosmics rates

    cosmics_rate = runsummary["cosmics_rate"]

    mask_cosmics = get_mask(cosmics_rate, ge=config.cosmics_ll, le=config.cosmics_ul)

    runsummary["mask_cosmics"] = mask_cosmics

    mask = runsummary["mask_cosmics"] & mask

    after_cosmics = np.count_nonzero(mask)
    s = (
        "After checking the rate of cosmics and selecting "
        "based on AGN Zoo Paper cuts, "
        f"{after_cosmics} runs are kept."
    )
    print(s)

    cosmics_rate_above10 = runsummary["cosmics_rate_above10"]
    cosmics_rate_above30 = runsummary["cosmics_rate_above30"]

    mask_above10 = get_mask(
        cosmics_rate_above10,
        le=config.cosmics_10_ul,
        ge=config.cosmics_10_ll,
    )
    mask_above30 = get_mask(
        cosmics_rate_above30,
        le=config.cosmics_30_ul,
        ge=config.cosmics_30_ll,
    )

    mask_above = mask_above10 & mask_above30
    runsummary["mask_cosmics_above"] = mask_above
    mask = runsummary["mask_cosmics_above"] & mask

    after_cosmics_above_n = np.count_nonzero(mask)
    s = (
        "After cutting on the rate of cosmics with more than 10 p.e. "
        f"(resp. 30 p.e.) {after_cosmics_above_n} runs are kept."
    )
    print(s)

    duration = np.sum(runsummary["elapsed_time"][mask].quantity).to(u.h)
    s = (
        f"A selected total of {len(runsummary)} runs add to a "
        f"duration of {duration:.2f} of data."
    )
    print(s)

    mask = np.in1d(runs["Run ID"], runsummary["runnumber"][mask])

    runs[mask].to_csv(args.output_runlist, index=False)

    runsummary.write(
        args.output_datachecks,
        serialize_meta=True,
        overwrite=True,
        path="data",
        compression=True,
    )
