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
from rich.progress import track

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()

pbar.SHOW_PROGRESS_BAR = True


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
    table["acceptance"] = 0.0
    table["acceptance_off"] = 0.0
    table.meta["NON_THR"] = 0
    table.meta["NOFF_THR"] = 0
    table.meta["ON_RA"] = position.icrs.ra
    table.meta["ON_DEC"] = position.icrs.dec
    return table


def main(config, output):  # noqa: PLR0915
    config = AnalysisConfig.read(config)

    analysis = Analysis(config)
    analysis.get_observations()

    on_region = analysis.config.datasets.on_region
    position = on_region_to_skyframe(on_region)

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
            config.datasets.geom.axes.energy.min.unit
        ),
        nbin=config.datasets.geom.axes.energy.nbins,
        unit=config.datasets.geom.axes.energy.min.unit,
        interp="log",
        node_type="edges",
    )

    # For calculating a significance. Could be configurable or be taken from irf
    threshold = 0.2 * u.deg
    # Here we could add more edges in principle, but these are guaranteed
    # to not overlap, so we can get the full histogram for free afterwards
    # as the sum of these, so I advocate to instead add further ones later
    # I do not intend to get smart with the caluculation of those aswell
    # for now as bins might only partially contribute to arbitrary ranges
    # The code below is a bit messy with the double loop, but avoids recalculating
    # everything for each energy bin and fills the total histogram as a side effect
    # which can take a while otherwise
    energy_lower = energy_axis.edges_min
    energy_upper = energy_axis.edges_max
    theta_table_all_energies = create_empty_table(theta_squared_axis, position)
    theta_table_all_energies.meta["ERANGE"] = "All energies"
    theta_tables = [
        create_empty_table(theta_squared_axis, position) for bin in energy_lower
    ]

    # The following is basically https://docs.gammapy.org/1.0.1/_modules/gammapy/makers/utils.html#make_theta_squared_table
    # Unfortunately gammapy does not allow energy slices, so we would need to
    # create new observations every time
    # This also allows to add some comments for the future :)
    alpha_tot = 0
    livetime_tot = 0
    for obs in track(analysis.observations):
        pos_angle = obs.pointing_radec.position_angle(position)
        sep_angle = obs.pointing_radec.separation(position)
        position_off = obs.pointing_radec.directional_offset_by(
            pos_angle + Angle(np.pi, "rad"), sep_angle
        )

        # Since we only create one off region, the acceptance between both
        # is always the same. This also simplifies the handling of the
        # total acceptance. Note, that I removed some code from
        # the gammapy function here making it less general, so
        # if we ever use multiple offset regions or have a different acceptance
        # in on and off regions (This here assumes radial symmetry), this code needs
        # to be revisited (but the normal gammapy code would not work either)
        # You could even argue, that the acceptance columns could be removed altogether,
        # but I think this is fine
        acceptance = np.ones(theta_squared_axis.nbin)
        acceptance_off = np.ones(theta_squared_axis.nbin)
        theta_table_all_energies["acceptance"] += acceptance
        theta_table_all_energies["acceptance_off"] += acceptance_off
        alpha = acceptance / acceptance_off
        alpha_tot += alpha * obs.observation_live_time_duration.to_value("s")
        livetime_tot += obs.observation_live_time_duration.to_value("s")

        # Select events in on/off regions
        separation = position.separation(obs.events.radec)
        separation_off = position_off.separation(obs.events.radec)
        mask_threshold_on = separation**2 < threshold
        mask_threshold_off = separation_off**2 < threshold

        # Behold the power of zip
        for low, high, table in zip(energy_lower, energy_upper, theta_tables):
            # Not really necessary, could do it in plotting as well
            if low > 1 * u.TeV:
                elow = low.to(u.TeV)
            else:
                elow = low.to(u.GeV)
            if high > 1 * u.TeV:
                ehigh = high.to(u.TeV)
            else:
                ehigh = high.to(u.GeV)
            table.meta["ERANGE"] = f"{elow:.2f} - {ehigh:.2f}"

            mask_energy = np.ones(len(obs.events.energy), dtype=bool)
            mask_energy &= obs.events.energy > elow
            mask_energy &= obs.events.energy < ehigh
            counts, _ = np.histogram(
                separation[mask_energy] ** 2, theta_squared_axis.edges
            )
            counts_off, _ = np.histogram(
                separation_off[mask_energy] ** 2, theta_squared_axis.edges
            )
            mask_on = mask_energy & mask_threshold_on
            mask_off = mask_energy & mask_threshold_off

            # cant go into the loop, because we only want the main table once
            table["acceptance"] += acceptance
            table["acceptance_off"] += acceptance_off
            for t in (table, theta_table_all_energies):
                t["counts"] += counts
                t["counts_off"] += counts_off
                t.meta["NON_THR"] += np.count_nonzero(mask_on)
                t.meta["NOFF_THR"] += np.count_nonzero(mask_off)

    alpha_tot /= livetime_tot
    hdulist = [fits.PrimaryHDU()]
    for i, t in enumerate([theta_table_all_energies] + theta_tables):
        t["alpha"] = alpha_tot
        stat = WStatCountsStatistic(t["counts"], t["counts_off"], t["alpha"])
        t["excess"] = stat.n_sig
        t["sqrt_ts"] = stat.sqrt_ts
        t["excess_errn"] = stat.compute_errn()
        t["excess_errp"] = stat.compute_errp()

        t.meta["ON_RA"] = position.icrs.ra
        t.meta["ON_DEC"] = position.icrs.dec
        hdulist.append(fits.table_to_hdu(t))

    fits.HDUList(hdulist).writeto(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
