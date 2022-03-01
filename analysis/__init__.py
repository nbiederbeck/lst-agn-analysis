from astropy.coordinates import SkyCoord
from gammapy.analysis import Analysis, AnalysisConfig


def get_analysis():
    config = AnalysisConfig.read("config.yaml")

    analysis = Analysis(config)
    analysis.get_observations()

    return analysis


def on_region_to_skyframe(on_region):
    if on_region.frame != "galactic":
        raise ValueError(f"Currently unsupported frame {on_region.frame}.")

    return SkyCoord(frame=on_region.frame, b=on_region.lat, l=on_region.lon)
