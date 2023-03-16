from argparse import ArgumentParser
from os import cpu_count

from astropy.coordinates import SkyCoord
from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import MapDataset
from gammapy.makers import (
    DatasetsMaker,
    ReflectedRegionsBackgroundMaker,
    SafeMaskMaker,
    SpectrumDatasetMaker,
    WobbleRegionsFinder,
)
from gammapy.maps import MapAxis, RegionGeom
from regions import PointSkyRegion

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("--n-off-regions", default=1, type=int)
parser.add_argument("-j", "--n-jobs", default=1, type=int)
args = parser.parse_args()


def main(config, output, n_off_regions, n_jobs):
    """
    Create dl4 datasets from a dl3 datastore for a pointlike analysis
    This can currently (Gammapy 0.20.1) not be done with the high-level interface
    as energy-dependent theta-cuts have just been added.
    """
    if n_jobs == 0:
        n_jobs = cpu_count()
    # Standard high-level interface stuff
    config = AnalysisConfig.read(config)
    analysis = Analysis(config)
    analysis.get_observations()

    # Define things for the dataset maker step
    # point sky region > circle sky region for energy dependent cuts
    on_region = analysis.config.datasets.on_region
    target_position = SkyCoord(frame=on_region.frame, b=on_region.lat, l=on_region.lon)

    on_region = PointSkyRegion(target_position)
    energy_axis_config = config.datasets.geom.axes.energy
    energy_axis = MapAxis.from_bounds(
        name="energy",
        lo_bnd=energy_axis_config.min.value,
        hi_bnd=energy_axis_config.max.to_value(energy_axis_config.min.unit),
        nbin=energy_axis_config.nbins,
        unit=energy_axis_config.min.unit,
        interp="log",
        node_type="edges",
    )
    geom = RegionGeom.create(region=on_region, axes=[energy_axis])
    dataset_maker = SpectrumDatasetMaker(
        containment_correction=False,
        selection=["counts", "exposure", "edisp"],
    )
    region_finder = WobbleRegionsFinder(n_off_regions=n_off_regions)
    bkg_maker = ReflectedRegionsBackgroundMaker(region_finder=region_finder)

    # use the energy threshold specified in the DL3 files
    # TODO Test what influence this has
    # according to docs most of these discard energy migration -> bad
    safe_mask_maker = SafeMaskMaker(methods=[])

    global_dataset = MapDataset.create(geom)

    makers = [
        dataset_maker,
        safe_mask_maker,
        bkg_maker,
    ]

    datasets_maker = DatasetsMaker(makers, stack_datasets=False, n_jobs=n_jobs)
    datasets = datasets_maker.run(
        global_dataset,
        analysis.observations,
        [
            MapDataset.create(geom, name=str(obs.obs_id))
            for obs in analysis.observations
        ],
    )

    datasets.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
