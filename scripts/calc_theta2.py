from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


from astropy.coordinates import SkyCoord
from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.makers.utils import make_theta_squared_table
from gammapy.maps import MapAxis


def on_region_to_skyframe(on_region):
    if on_region.frame != "galactic":
        raise ValueError(f"Currently unsupported frame {on_region.frame}.")

    return SkyCoord(frame=on_region.frame, b=on_region.lat, l=on_region.lon)


def main(config, output):
    theta2_axis = MapAxis.from_bounds(
        0,
        0.2,
        nbin=20,
        interp="lin",
        unit="deg2",
    )

    config = AnalysisConfig.read(config)

    analysis = Analysis(config)
    analysis.get_observations()

    on_region = analysis.config.datasets.on_region
    position = on_region_to_skyframe(on_region)

    observations = analysis.observations
    theta2_table = make_theta_squared_table(
        observations=observations,
        position=position,
        theta_squared_axis=theta2_axis,
    )

    theta2_table.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
