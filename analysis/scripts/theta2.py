from analysis import get_analysis, on_region_to_skyframe
from gammapy.makers.utils import make_theta_squared_table
from gammapy.maps import MapAxis
from gammapy.visualization import plot_theta_squared_table
from matplotlib import pyplot as plt


def main():
    analysis = get_analysis()

    on_region = analysis.config.datasets.on_region
    position = on_region_to_skyframe(on_region)

    theta2_axis = MapAxis.from_bounds(0, 0.2, nbin=20, interp="lin", unit="deg2")

    observations = analysis.observations
    theta2_table = make_theta_squared_table(
        observations=observations,
        position=position,
        theta_squared_axis=theta2_axis,
    )

    plot_theta_squared_table(theta2_table)

    plt.savefig("build/theta2.pdf")
