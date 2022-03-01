from analysis import get_analysis, on_region_to_skyframe
from gammapy.data import EventList
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def main():
    analysis = get_analysis()

    events = EventList.from_stack([obs.events for obs in analysis.observations])

    center = on_region_to_skyframe(analysis.config.datasets.on_region)

    with PdfPages("build/observation_plots.pdf") as pdf:
        events.plot_image()
        pdf.savefig()

        fig, ax = plt.subplots()
        events.plot_offset2_distribution(ax=ax, center=center)
        pdf.savefig()

        fig, ax = plt.subplots()
        events.plot_energy()
        pdf.savefig()

        fig, ax = plt.subplots()
        events.plot_time()
        pdf.savefig()
