from argparse import ArgumentParser

from astroplan.moon import moon_illumination
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, get_moon, get_sun
from astropy.table import Table
from astropy.time import Time
from config import Config
from matplotlib import colors
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("-o", "--output_path", required=True)
parser.add_argument("-c", "--config", required=True)
args = parser.parse_args()

config = Config.parse_file(args.config)


def main():
    runsummary = Table.read(args.input_path)
    runsummary = runsummary[runsummary["mask_run_selection"]]
    time = Time(runsummary["time"], format="unix", scale="utc")

    cmap = plt.cm.afmhot
    norm = colors.Normalize(0, 1)

    location = EarthLocation.of_site("lapalma")

    ped_std = runsummary["ped_charge_stddev"]

    altaz = AltAz(obstime=time, location=location)

    get_sun(time).transform_to(altaz)
    moon = get_moon(time, location=location).transform_to(altaz)

    moon_light = moon_illumination(time)
    moon_light[moon.alt.to_value(u.deg) < 0] = 1

    fig, ax = plt.subplots()

    im = ax.scatter(
        moon.alt.to_value(u.deg),
        ped_std,
        label="Runs",
        c=moon_light,
        cmap=cmap,
        norm=norm,
        edgecolor="k",
    )

    ax.set_ylim(0)
    ax.set_xlim(-90, 80)

    ax.fill_between(
        (0, 1),
        [config.pedestal_ll],
        [config.pedestal_ul],
        alpha=0.1,
        label="Selection",
        transform=ax.get_yaxis_transform(),
    )

    ax.set_ylabel("Pedestal Charge Std.Dev. / p.e.")
    ax.set_xlabel("Altitude / deg")

    fig.colorbar(im, ax=ax, label="Moon Illumination")

    ax.legend()

    fig.savefig(args.output_path)


if __name__ == "__main__":
    main()
