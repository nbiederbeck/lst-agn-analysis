from gammapy.analysis import Analysis, AnalysisConfig
from matplotlib import pyplot as plt


def main():
    config = AnalysisConfig.read("configs/config.yaml")

    analysis = Analysis(config)
    analysis.get_observations()

    analysis.config.datasets.stack = False
    analysis.get_datasets()

    analysis.read_models("build/model-best-fit.yaml")

    analysis.get_light_curve()

    fig, ax = plt.subplots()
    analysis.light_curve.plot(ax=ax, axis_name="time")
    fig.savefig("build/light_curve.pdf")
