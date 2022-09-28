from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("--n-off-regions", default=1)
args = parser.parse_args()


from astropy.coordinates import SkyCoord
from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets, SpectrumDataset
from gammapy.makers import (
    ReflectedRegionsBackgroundMaker,
    SafeMaskMaker,
    SpectrumDatasetMaker,
    WobbleRegionsFinder,
)
from gammapy.maps import Map, MapAxis, RegionGeom
from regions import PointSkyRegion
from tqdm.auto import tqdm


def main(config, output, n_off_regions):
    """
    Create dl4 datasets from a dl3 datastore for a pointlike analysis
    This can currently (Gammapy 0.20.1) not be done with the high-level interface
    as energy-dependent theta-cuts have just been added.
    """
    # Standard high-level interface stuff
    config = AnalysisConfig.read(config)
    analysis = Analysis(config)
    analysis.get_observations()

    # Define things for the dataset maker step
    # point sky region > circle sky region for energy dependent cuts
    on_region = analysis.config.datasets.on_region
    target_position = SkyCoord(frame=on_region.frame, b=on_region.lat, l=on_region.lon)

    on_region = PointSkyRegion(target_position)
    energy_axis = MapAxis.from_bounds(
        name="energy",
        lo_bnd=config.datasets.geom.axes.energy.min.value,
        hi_bnd=config.datasets.geom.axes.energy.max.to_value(
            config.datasets.geom.axes.energy.min.unit
        ),
        nbin=config.datasets.geom.axes.energy.nbins,
        unit=config.datasets.geom.axes.energy.min.unit,
        interp="log",
        node_type="edges",
    )
    energy_axis_true = MapAxis.from_bounds(
        name="energy_true",
        lo_bnd=config.datasets.geom.axes.energy_true.min.value,
        hi_bnd=config.datasets.geom.axes.energy_true.max.to_value(
            config.datasets.geom.axes.energy_true.min.unit
        ),
        nbin=config.datasets.geom.axes.energy_true.nbins,
        unit=config.datasets.geom.axes.energy_true.min.unit,
        interp="log",
        node_type="edges",
    )
    geom = RegionGeom.create(region=on_region, axes=[energy_axis])
    dataset_empty = SpectrumDataset.create(geom=geom, energy_axis_true=energy_axis_true)
    dataset_maker = SpectrumDatasetMaker(
        containment_correction=False, selection=["counts", "exposure", "edisp"]
    )
    region_finder = WobbleRegionsFinder(n_off_regions=n_off_regions)
    bkg_maker = ReflectedRegionsBackgroundMaker(region_finder=region_finder)

    # use the energy threshold specified in the DL3 files
    # TODO Test what influence this has
    safe_mask_masker = SafeMaskMaker(methods=["aeff-default"])

    # Create datasets from each observation
    datasets = Datasets()
    counts = Map.create(skydir=target_position, width=3)
    for observation in tqdm(analysis.observations):
        dataset = dataset_maker.run(
            dataset_empty.copy(name=str(observation.obs_id)), observation
        )
        counts.fill_events(observation.events)
        dataset_on_off = bkg_maker.run(dataset, observation)
        dataset_on_off = safe_mask_masker.run(dataset_on_off, observation)
        datasets.append(dataset_on_off)

    datasets.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
