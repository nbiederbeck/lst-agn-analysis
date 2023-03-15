import json
from argparse import ArgumentParser
from itertools import chain

import astropy.units as u
import numpy as np
from astropy.coordinates import AltAz, EarthLocation
from astropy.table import Table
from astropy.time import Time

parser = ArgumentParser()
parser.add_argument("--runs", required=True)
parser.add_argument("--runsummary", required=True)
parser.add_argument("-o", "--output-path", required=True)
args = parser.parse_args()

with open(args.runs, "r") as f:
    runs = json.load(f)


@u.quantity_input
def build_altaz(*, alt: u.deg = None, zd: u.deg = None, az: u.deg = None) -> AltAz:
    """Build AltAz from zenith distance and azimuth.

    This function exists to make no mistakes when translating
    zenith distance to altitude.

    Altitude takes precedence over zenith, if given both.

    location and obstime is needed for transformations with
    astropy version 4.3.1

    Obstime is fixed.
    """
    if alt is None:
        if zd is None:
            raise ValueError("Specify either alt or zd")
        zenith = u.Quantity(90, u.deg)
        alt = zenith - zd

    location = EarthLocation.of_site("lapalma")
    obstime = Time("2022-01-01T00:00")

    return AltAz(alt=alt, az=az, location=location, obstime=obstime)


def get_theta_az_from_node(node: str) -> np.ndarray:
    """Strip theta and az from name of node.

    `node` must be of kind 'node_theta_10.0_az_102.199_'.
    """
    _, _, theta, _, az, _ = node.split("_")
    return np.array([theta, az], dtype=float)


def get_pointings_of_irfs(filelist) -> AltAz:
    """From the list of directory names with AllSky IRFs,
    build the AltAz frame with pointings.

    The names are of kind 'node_theta_10.0_az_102.199_'.
    """
    theta, az = np.array([get_theta_az_from_node(f) for f in filelist]).T

    return build_altaz(zd=theta * u.deg, az=az * u.deg)


def main() -> None:
    run_ids = list(chain(*runs.values()))
    runsummary = Table.read(args.runsummary)

    mask = np.in1d(runsummary["runnumber"], run_ids)

    pointings = AltAz(
        alt=u.Quantity(runsummary[mask]["mean_altitude"].value, u.rad),
        az=u.Quantity(runsummary[mask]["mean_azimuth"].value, u.rad),
    )

    wrap_angles = u.Quantity([0, 90, 180, 270, 360], u.deg, dtype="int")
    table = Table(
        {
            f"az_wrap_at_{i.to_value(u.deg):03d}": pointings.az.wrap_at(i)
            for i in wrap_angles
        }
    )
    table["alt"] = pointings.alt
    table["zen"] = pointings.zen
    table.write(args.output_path, overwrite=True)


if __name__ == "__main__":
    main()
