import json
import logging
from argparse import ArgumentParser

import astropy.units as u
import numpy as np
from astropy.coordinates import Angle, SkyCoord
from astropy.io import fits
from astropy.table import Table
from gammapy.data import DataStore
from gammapy.maps import MapAxis
from gammapy.stats import WStatCountsStatistic
from gammapy.utils import pbar
from log import setup_logging

pbar.SHOW_PROGRESS_BAR = True


def format_energy(e):
    if e > 1 * u.TeV:
        e = e.to(u.TeV)
    else:
        e = e.to(u.GeV)
    return f"{e:.1f}"


def create_empty_table(theta_squared_axis, position):
    table = Table()
    table["theta2_min"] = theta_squared_axis.edges_min
    table["theta2_max"] = theta_squared_axis.edges_max
    table["counts"] = 0
    table["counts_off"] = 0

    # This is very minimal, assuming perfectly matching acceptance in on / off
    table["acceptance"] = 1.0
    table["acceptance_off"] = 1.0
    table["alpha"] = 1.0

    # Cant save angle objects in fits header
    table.meta["ON_RA"] = position.icrs.ra.to_string()
    table.meta["ON_DEC"] = position.icrs.dec.to_string()
    return table


def get_axes(obs):
    """
    Create axes for the theta table.
    Energy axis is taken from the radmax table
    in the observation in order to match cut from
    the irfs.
    """
    theta_squared_axis = MapAxis.from_bounds(
        0,
        0.2,
        nbin=20,
        interp="lin",
        unit="deg2",
    )
    energy_axis = obs.rad_max.axes["energy"]
    return theta_squared_axis, energy_axis


def stack_energies(tables):
    """
    Sum counts, recalculate sqrt ts, excess, ...
    Since every table is from the same observation(s),
    we do not need to handle acceptance and metadata.
    """
    stacked = tables[0].copy()
    for t in tables[1:]:
        for c in ["counts", "counts_off"]:
            stacked[c] += t[c]
    stacked = add_stats(stacked)
    return stacked


def add_stats(table):
    "Calculate sqrt ts and excess."
    stat = WStatCountsStatistic(table["counts"], table["counts_off"], table["alpha"])
    table["excess"] = stat.n_sig
    table["sqrt_ts"] = stat.sqrt_ts
    table["excess_errn"] = stat.compute_errn()
    table["excess_errp"] = stat.compute_errp()
    return table


def main(input_dir, output, obs_id, log_file, verbose, config):  # noqa: PLR0915 PLR0913
    """
    Basically this:
    https://docs.gammapy.org/1.0.1/_modules/gammapy/makers/utils.html#make_theta_squared_table
    for one observation and in bins of energy
    """
    setup_logging(logfile=log_file, verbose=verbose)
    log = logging.getLogger("theta2-per-obs")
    ds = DataStore.from_dir(input_dir)
    obs = ds.obs(int(obs_id), ["aeff"])

    theta_squared_axis, energy_axis = get_axes(obs)
    underflow = -np.inf * u.GeV
    overflow = np.inf * u.GeV
    energy_lower = np.append(
        np.append(underflow, energy_axis.edges_min),
        energy_axis.edges_max[-1],
    )
    energy_upper = np.append(
        np.append(energy_axis.edges_min[0], energy_axis.edges_max),
        overflow,
    )
    # This will break for multiple offsets in the IRF
    theta_cuts = np.append(None, np.append(obs.rad_max.data.flatten(), None))

    # Get on and off position
    with open(config) as f:
        config = json.load(f)
    position = SkyCoord(
        frame="icrs",
        ra=config["source_ra_deg"] * u.deg,
        dec=config["source_dec_deg"] * u.deg,
    )
    pos_angle = obs.pointing_radec.position_angle(position)
    sep_angle = obs.pointing_radec.separation(position)
    position_off = obs.pointing_radec.directional_offset_by(
        pos_angle + Angle(np.pi, "rad"),
        sep_angle,
    )

    # Distance to on and off positions
    separation = position.separation(obs.events.radec)
    separation_off = position_off.separation(obs.events.radec)

    hdulist = [fits.PrimaryHDU()]
    theta_tables = []
    for elow, ehigh, theta in zip(energy_lower, energy_upper, theta_cuts):
        log.info("Calculating counts in range {elow} - {ehigh}")
        table = create_empty_table(theta_squared_axis, position)
        # Useful for plotting
        table.meta["ELOW"] = format_energy(elow)
        table.meta["EHI"] = format_energy(ehigh)
        table.meta["CUT"] = theta**2 if theta else ""
        # This is needed for stacking later
        table.meta["TOBS"] = obs.observation_live_time_duration.to_value(u.s)

        mask_energy = (obs.events.energy >= elow) & (obs.events.energy < ehigh)
        table["counts"], _ = np.histogram(
            separation[mask_energy] ** 2,
            theta_squared_axis.edges,
        )
        table["counts_off"], _ = np.histogram(
            separation_off[mask_energy] ** 2,
            theta_squared_axis.edges,
        )

        table = add_stats(table)
        hdulist.append(fits.table_to_hdu(table))
        theta_tables.append(table)

    stacked = stack_energies(theta_tables)
    stacked.meta["ELOW"] = format_energy(underflow)
    stacked.meta["EHI"] = format_energy(overflow)
    hdulist.append(fits.table_to_hdu(stacked))
    fits.HDUList(hdulist).writeto(output, overwrite=True)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input-dir", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--obs-id", required=True)
    parser.add_argument("--log-file")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-c", "--config", required=True)
    args = parser.parse_args()

    main(**vars(args))
