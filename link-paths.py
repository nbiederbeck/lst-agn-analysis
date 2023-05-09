import json
from argparse import ArgumentParser
from itertools import chain
from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.coordinates import AltAz, EarthLocation, angular_separation
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

build_dir = Path(args.output_path).parent
outdir_dl1 = build_dir / "dl1/"
filename_dl1 = "dl1_LST-1.Run{run_id}.h5"
template_target_dl1 = (
    (Path("/fefs/aswg/data/real/DL1/{night}/v0.9/tailcut84") / filename_dl1)
    .resolve()
    .as_posix()
)
template_linkname_dl1 = (outdir_dl1 / filename_dl1).resolve().as_posix()

outdir_dl2 = build_dir / "dl2/test/"
filename_dl2 = "dl2_LST-1.Run{run_id}.h5"
template_target_dl2 = "/fefs/aswg/data/mc/DL2/AllSky/{prod}/TestingDataset/{dec}/{node}/dl2_{prod}_{node}_merged.h5"  # noqa
template_linkname_dl2 = (outdir_dl2 / filename_dl2).resolve().as_posix()

filename_irf = "irf_Run{run_id}.fits.gz"
template_irf = "/fefs/aswg/data/mc/IRF/AllSky/{prod}/TestingDataset/{dec}/{node}/irf_{prod}_{node}.fits.gz"  # noqa

outdir_model = build_dir / "models/model_Run{run_id}/"
template_target_model = "/fefs/aswg/data/models/AllSky/{prod}/{dec}/"
template_linkname_model = outdir_model.resolve().as_posix()


def sin_delta(altaz: AltAz):
    """Delta is the angle between pointing and magnetic field."""
    # Values from
    # https://geomag.bgs.ac.uk/data_service/models_compass/igrf_calc.html
    # for La Palma coordinates and date=2021-12-01.
    #
    # Also used here:
    # https://github.com/cta-observatory/lst-sim-config/issues/2
    b_inc = u.Quantity(-37.36, u.deg)
    b_dec = u.Quantity(-4.84, u.deg)

    delta = angular_separation(
        lon1=altaz.az,
        lat1=altaz.alt,
        lon2=b_dec,
        lat2=b_inc,
    )
    return np.sin(delta.to_value(u.rad))


def cos_zenith(altaz: AltAz):
    return np.cos(altaz.zen.to_value(u.rad))


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

    location = EarthLocation.from_geodetic(
        u.Quantity(-17.89139, u.deg),
        u.Quantity(28.76139, u.deg),
        height=u.Quantity(2184, u.m),
    )
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


def euclidean_distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def main() -> None:
    prod = args.prod
    dec = args.dec

    runsummary = Table.read(args.runsummary)

    path = Path(template_irf.format(prod=prod, dec=dec, node=""))
    filelist = [p.name for p in path.parent.iterdir()]
    irf_pointings: AltAz = get_pointings_of_irfs(filelist)

    irf_sindelta = sin_delta(irf_pointings)
    irf_coszenith = cos_zenith(irf_pointings)

    progress = tqdm(total=n_runs)

    for night, run_ids in runs.items():
        for run_id in run_ids:
            target_dl1 = Path(template_target_dl1.format(night=night, run_id=run_id))

            run = runsummary[runsummary["runnumber"] == int(run_id)]

            pointing = build_altaz(
                alt=run["mean_altitude"] * u.rad,
                az=run["mean_azimuth"] * u.rad,
            )
            sindelta = sin_delta(pointing)
            coszenith = cos_zenith(pointing)

            nearest_irf = euclidean_distance(
                x1=sindelta,
                y1=coszenith,
                x2=irf_sindelta,
                y2=irf_coszenith,
            ).argmin()
            node = filelist[nearest_irf]

            linkname_dl1 = Path(
                template_linkname_dl1.format(
                    night=night,
                    run_id=run_id,
                ),
            )

            target_model = Path(template_target_model.format(prod=prod, dec=dec))
            linkname_model = Path(template_linkname_model.format(run_id=run_id))

            target_dl2 = Path(template_target_dl2.format(prod=prod, dec=dec, node=node))
            linkname_dl2 = Path(template_linkname_dl2.format(run_id=run_id))

            linkname_dl1.parent.mkdir(exist_ok=True, parents=True)
            if linkname_dl1.exists() and linkname_dl1.is_symlink():
                linkname_dl1.unlink()
            linkname_dl1.symlink_to(target_dl1)

            linkname_dl2.parent.mkdir(exist_ok=True, parents=True)
            if linkname_dl2.exists() and linkname_dl2.is_symlink():
                linkname_dl2.unlink()
            linkname_dl2.symlink_to(target_dl2)

            linkname_model.parent.mkdir(exist_ok=True, parents=True)
            if linkname_model.exists() and linkname_model.is_symlink():
                linkname_model.unlink()
            linkname_model.symlink_to(target_model)

            progress.update()

    Path(args.output_path).touch()


if __name__ == "__main__":
    main()
