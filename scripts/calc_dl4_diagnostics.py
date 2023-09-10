from argparse import ArgumentParser

import astropy.units as u
import numpy as np
from astropy.io import fits
from astropy.table import Table
from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("--dataset-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(config, dataset_path, output):
    config = AnalysisConfig.read(config)
    analysis = Analysis(config)
    analysis.get_observations()

    datasets = Datasets.read(dataset_path)
    hdulist = [fits.PrimaryHDU()]

    # vs livetime
    info_table = datasets.info_table(cumulative=True)
    table = Table(
        {
            "excess": info_table["excess"],
            "sqrt_ts": info_table["sqrt_ts"],
            "livetime": info_table["livetime"],
        },
    )
    table.meta["CUMUL"] = True
    hdulist.append(fits.table_to_hdu(table))

    # vs run id and vs zenith
    # this requires the datasets to not be stacked
    if len(analysis.observations) == len(datasets):
        obs_ids = []
        excess = []
        zenith = []
        sqrt_ts = []
        for obs, ds in zip(analysis.observations, datasets):
            obs_ids.append(obs.obs_id)
            #zenith.append(obs.get_pointing_altaz(obs.tstart).zen.to_value(u.deg))

            excess.append(ds.info_dict()["excess"])
            sqrt_ts.append(ds.info_dict()["sqrt_ts"])
        table = Table(
            {
                "excess": np.array(excess),
                "sqrt_ts": np.array(sqrt_ts),
                #"zenith": np.array(zenith),
                "obs_id": np.array(obs_ids),
            },
        )
        table.meta["CUMUL"] = False
        hdulist.append(fits.table_to_hdu(table))

    fits.HDUList(hdulist).writeto(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
