from argparse import ArgumentParser

import astropy.units as u
import numpy as np
from astropy.coordinates import Angle, SkyCoord
from astropy.io import fits
from astropy.table import Table
from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.maps import MapAxis
from gammapy.stats import WStatCountsStatistic
from gammapy.utils import pbar

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("--obs-id", required=True)
args = parser.parse_args()

pbar.SHOW_PROGRESS_BAR = True


def format_energy(e):
    if e > 1 * u.TeV:
        e = e.to(u.TeV)
    else:
        e = e.to(u.GeV)
    return f"{e:.1f}"


def on_region_to_skyframe(on_region):
    if on_region.frame != "galactic":
        raise ValueError(f"Currently unsupported frame {on_region.frame}.")

    return SkyCoord(frame=on_region.frame, b=on_region.lat, l=on_region.lon)


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


def get_axes(config):
    theta_squared_axis = MapAxis.from_bounds(
        0,
        0.2,
        nbin=20,
        interp="lin",
        unit="deg2",
    )
    # TODO: Is there an easier way to just get the axes, that is used in the analysis?
    energy_axis = MapAxis.from_bounds(
        name="energy",
        lo_bnd=config.datasets.geom.axes.energy.min.value,
        hi_bnd=config.datasets.geom.axes.energy.max.to_value(
            config.datasets.geom.axes.energy.min.unit,
        ),
        nbin=config.datasets.geom.axes.energy.nbins,
        unit=config.datasets.geom.axes.energy.min.unit,
        interp="log",
        node_type="edges",
    )
    return theta_squared_axis, energy_axis


def stack_energies(tables):
    """
    Sum counts, recalculate sqrt ts, excess, ...
    Since every table is from the same observation(s),
    we do not need to handle acceptance and metadata.
    """
    for i, t in enumerate(tables):
        if i == 0:
            stacked = t.copy()
        else:
            for c in ["counts", "counts_off"]:
                stacked[c] += t[c]
    stacked = add_stats(stacked)
    return stacked


def add_stats(table):
    stat = WStatCountsStatistic(table["counts"], table["counts_off"], table["alpha"])
    table["excess"] = stat.n_sig
    table["sqrt_ts"] = stat.sqrt_ts
    table["excess_errn"] = stat.compute_errn()
    table["excess_errp"] = stat.compute_errp()
    return table


def main(config, output, obs_id):  # noqa: PLR0915
    """
    Basically this:
    https://docs.gammapy.org/1.0.1/_modules/gammapy/makers/utils.html#make_theta_squared_table
    for one observation and in bins of energy
    """
    config = AnalysisConfig.read(config)

    analysis = Analysis(config)
    analysis.get_observations()
    obs = analysis.observations[obs_id]

    theta_squared_axis, energy_axis = get_axes(config)
    underflow = -np.inf * u.GeV
    overflow = np.inf * u.GeV
    print(energy_axis.edges_max)
    print(energy_axis.edges_max[-1])
    energy_lower = np.append(
        np.append(underflow, energy_axis.edges_min),
        energy_axis.edges_max[-1],
    )
    energy_upper = np.append(
        np.append(energy_axis.edges_min[0], energy_axis.edges_max),
        overflow,
    )

    # Get on and off position
    on_region = analysis.config.datasets.on_region
    position = on_region_to_skyframe(on_region)
    pos_angle = obs.pointing_radec.position_angle(position)
    sep_angle = obs.pointing_radec.separation(position)
    position_off = obs.pointing_radec.directional_offset_by(
        pos_angle + Angle(np.pi, "rad"),
        sep_angle,
    )

    # Distance to an and off positions
    separation = position.separation(obs.events.radec)
    separation_off = position_off.separation(obs.events.radec)

    hdulist = [fits.PrimaryHDU()]
    theta_tables = []
    for elow, ehigh in zip(energy_lower, energy_upper):
        print("Calculating counts in range", elow, ehigh)
        table = create_empty_table(theta_squared_axis, position)
        # Useful for plotting
        table.meta["ELOW"] = format_energy(elow)
        table.meta["EHI"] = format_energy(ehigh)
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
    main(**vars(args))
