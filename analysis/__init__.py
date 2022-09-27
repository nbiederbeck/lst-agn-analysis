from astropy.coordinates import SkyCoord
from gammapy.analysis import Analysis, AnalysisConfig


def get_analysis():
    raise Exception
    config = AnalysisConfig.read("configs/config.yaml")

    analysis = Analysis(config)
    analysis.get_observations()

    return analysis
