from analysis import get_analysis
from matplotlib import pyplot as plt


def main():
    analysis = get_analysis()

    analysis.config.datasets.stack = False
    analysis.get_datasets()

    analysis.read_models("build/model-best-fit.yaml")

    analysis.get_light_curve()

    fig, ax = plt.subplots()
    analysis.light_curve.plot(ax=ax, axis_name="time")
    fig.savefig("build/light_curve.pdf")
