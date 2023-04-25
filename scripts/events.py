from argparse import ArgumentParser

from astropy.coordinates import SkyCoord
from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.data import EventList
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def on_region_to_skyframe(on_region):
    return SkyCoord(on_region.lon, on_region.lat, frame=on_region.frame)


def main(config, output):
    config = AnalysisConfig.read(config)

    analysis = Analysis(config)
    analysis.get_observations()

    events = EventList.from_stack(
        [obs.events for obs in analysis.observations],
        metadata_conflicts="silent",
    )

    center = on_region_to_skyframe(analysis.config.datasets.on_region)

    with PdfPages(output) as pdf:
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


if __name__ == "__main__":
    main(**vars(args))
