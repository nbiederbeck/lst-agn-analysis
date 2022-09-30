from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-o', '--output', required=True)
args = parser.parse_args()
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.info("Logging.")

from astropy.coordinates import SkyCoord
from gammapy.analysis import Analysis, AnalysisConfig
import numpy as np
from gammapy.makers.utils import make_theta_squared_table
from gammapy.maps import MapAxis
from gammapy.visualization import plot_theta_squared_table
from matplotlib import pyplot as plt


def on_region_to_skyframe(on_region):
    if on_region.frame != "galactic":
        raise ValueError(f"Currently unsupported frame {on_region.frame}.")

    return SkyCoord(frame=on_region.frame, b=on_region.lat, l=on_region.lon)


def main(output):
    config = AnalysisConfig.read("configs/config.yaml")

    analysis = Analysis(config)
    analysis.get_observations()

    log.info("Got observations")

    on_region = analysis.config.datasets.on_region
    position = on_region_to_skyframe(on_region)

    theta2_axis = MapAxis.from_bounds(0, 0.2, nbin=20, interp="lin", unit="deg2")

    observations = analysis.observations
    theta2_table = make_theta_squared_table(
        observations=observations,
        position=position,
        theta_squared_axis=theta2_axis,
    )

    log.info("Plotting ...")

    fig, ax = plt.subplots()

    x = theta2_axis.center.value
    ax.errorbar(x, theta2_table['counts'], yerr=np.sqrt(theta2_table['counts']), label='counts', linestyle='')
    ax.errorbar(x, theta2_table['counts_off'], yerr=np.sqrt(theta2_table['counts_off']), label='counts off', linestyle='')

    plt.savefig(output)


if __name__ == "__main__":
    main(vars(args))
