import re
from pathlib import Path

import astropy.units as u
import numpy as np
import tables
from astropy.coordinates import AltAz, EarthLocation
from astropy.time import Time
from tqdm import tqdm

from run_ids import mrk421, one_es1959

sources = {
    "mrk421": mrk421,
    "one_es1959": one_es1959,
}

outdir = "build/dl1/{source}/"
filename = "dl1_LST-1.Run{run_id:05d}.h5"
template_target = "/fefs/aswg/data/real/DL1/{night}/v0.9/tailcut84/" + filename
template_linkname = outdir + filename

base_irf = Path("/fefs/aswg/data/mc/IRF/AllSky/")
base_mc = Path("/fefs/aswg/data/models/AllSky/")
template_irf = "{prod}/TestingDataset/{dec}/"
template_mc = "{prod}/{dec}/"
path = Path(
    "/fefs/aswg/data/mc/IRF/AllSky/20221027_v0.9.9_crab_tuned/TestingDataset/dec_2276"
)


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


def get_pointing_of_run(path: Path) -> AltAz:
    """Get the mean telescope position of a single run."""
    with tables.open_file(
        path, root_uep="/dl1/event/telescope/parameters", mode="r"
    ) as f:
        table = f.get_node("/LST_LSTCam")
        zd_mean = u.Quantity(table.col("alt_tel").mean(), u.rad)
        az_mean = u.Quantity(table.col("az_tel").mean(), u.rad)
    return build_altaz(zd=zd_mean, az=az_mean)


def get_pointings_of_irfs(filelist) -> AltAz:
    """From the list of directory names with AllSky IRFs,
    build the AltAz frame with pointings.

    The names are of kind 'node_theta_10.0_az_102.199_',
    and the numbers are extracted via regex.
    """
    decimal = re.compile(r"\d+.\d+")
    theta, az = np.array([list(map(float, re.findall(decimal, f))) for f in filelist]).T

    return build_altaz(zd=theta * u.deg, az=az * u.deg)


def main():
    prod = "20221027_v0.9.9_crab_tuned"
    dec = "dec_2276"

    path = base_irf / template_irf.format(prod=prod, dec=dec)
    filelist = [p.name for p in path.iterdir()]
    irf_pointings: AltAz = get_pointings_of_irfs(filelist)

    verbose = False
    for name, source in tqdm(sources.items(), disable=not verbose):
        for night, run_ids in tqdm(source.items(), position=1, disable=not verbose):
            for run_id in tqdm(run_ids, position=2, disable=not verbose):
                target = template_target.format(night=night, run_id=run_id)

                pointing: AltAz = get_pointing_of_run(target)
                nearest_irf = pointing.separation(irf_pointings).argmin()
                node = filelist[nearest_irf]

                linkname = Path(
                    template_linkname.format(
                        night=night,
                        run_id=run_id,
                        source=name,
                    )
                )

                # link irf
                # link model

                if not linkname.is_file():
                    # print(linkname)
                    print(path / node)
                    linkname.parent.mkdir(exist_ok=True, parents=True)
                    linkname.symlink_to(target)


if __name__ == "__main__":
    main()
