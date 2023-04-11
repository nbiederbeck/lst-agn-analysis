import json
from argparse import ArgumentParser
from itertools import chain
from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.coordinates import AltAz, EarthLocation
from astropy.table import Table
from astropy.time import Time
from tqdm import tqdm

parser = ArgumentParser()
parser.add_argument("--runs", required=True)
parser.add_argument("--prod", required=True)
parser.add_argument("--dec", required=True)
parser.add_argument("--runsummary", required=True)
parser.add_argument("-o", "--output-path", required=True)
args = parser.parse_args()

with open(args.runs, "r") as f:
    runs = json.load(f)
n_runs = len(set(chain(*runs.values())))

outdir_dl1 = "build/dl1/"
filename_dl1 = "dl1_LST-1.Run{run_id:05d}.h5"
template_target_dl1 = "/fefs/aswg/data/real/DL1/{night}/v0.9/tailcut84/" + filename_dl1
template_linkname_dl1 = outdir_dl1 + filename_dl1

outdir_dl2 = "build/dl2/test/"
filename_dl2 = "dl2_LST-1.Run{run_id:05d}.h5"
template_target_dl2 = "/fefs/aswg/data/mc/DL2/AllSky/{prod}/TestingDataset/{dec}/{node}/dl2_{prod}_{node}_merged.h5"  # noqa
template_linkname_dl2 = outdir_dl2 + filename_dl2

outdir_irf = "build/irf/"
filename_irf = "irf_Run{run_id:05d}.fits.gz"
template_target_irf = "/fefs/aswg/data/mc/IRF/AllSky/{prod}/TestingDataset/{dec}/{node}/irf_{prod}_{node}.fits.gz"  # noqa
template_linkname_irf = outdir_irf + filename_irf

outdir_model = "build/models/model_Run{run_id:05d}/"
template_target_model = "/fefs/aswg/data/models/AllSky/{prod}/{dec}/"
template_linkname_model = outdir_model


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
    prod = args.prod
    dec = args.dec

    runsummary = Table.read(args.runsummary)

    path = Path(template_target_irf.format(prod=prod, dec=dec, node=""))
    filelist = [p.name for p in path.parent.iterdir()]
    irf_pointings: AltAz = get_pointings_of_irfs(filelist)

    progress = tqdm(total=n_runs)

    for night, run_ids in runs.items():
        for run_id in run_ids:
            target_dl1 = Path(template_target_dl1.format(night=night, run_id=run_id))

            run = runsummary[runsummary["runnumber"] == run_id]

            pointing = build_altaz(
                alt=run["mean_altitude"] * u.rad,
                az=run["mean_azimuth"] * u.rad,
            )
            nearest_irf = pointing.separation(irf_pointings).argmin()
            node = filelist[nearest_irf]

            linkname_dl1 = Path(
                template_linkname_dl1.format(
                    night=night,
                    run_id=run_id,
                )
            )

            target_irf = Path(template_target_irf.format(prod=prod, dec=dec, node=node))
            linkname_irf = Path(template_linkname_irf.format(run_id=run_id))

            target_model = Path(template_target_model.format(prod=prod, dec=dec))
            linkname_model = Path(template_linkname_model.format(run_id=run_id))

            target_dl2 = Path(template_target_dl2.format(prod=prod, dec=dec, node=node))
            linkname_dl2 = Path(template_linkname_dl2.format(run_id=run_id))

            if not linkname_dl1.exists():
                linkname_dl1.parent.mkdir(exist_ok=True, parents=True)
                linkname_dl1.symlink_to(target_dl1)

            if not linkname_dl2.exists():
                linkname_dl2.parent.mkdir(exist_ok=True, parents=True)
                linkname_dl2.symlink_to(target_dl2)

            if not linkname_irf.exists():
                linkname_irf.parent.mkdir(exist_ok=True, parents=True)
                linkname_irf.symlink_to(target_irf)

            if not linkname_model.exists():
                linkname_model.parent.mkdir(exist_ok=True, parents=True)
                linkname_model.symlink_to(target_model)

            progress.update()

    Path(args.output_path).touch()


if __name__ == "__main__":
    main()
