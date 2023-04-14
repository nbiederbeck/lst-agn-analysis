from argparse import ArgumentParser

from gammapy.datasets import Datasets
from gammapy.estimators import SensitivityEstimator
from gammapy.modeling.models import create_crab_spectral_model

parser = ArgumentParser()
parser.add_argument("--dataset-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(dataset_path, output):
    datasets = Datasets.read(dataset_path)
    # in case we didnt stack before
    stacked = datasets.stack_reduce()

    # CTA Requirements
    est = SensitivityEstimator(
        spectrum=create_crab_spectral_model(),
        gamma_min=10,
        n_sigma=5,
        bkg_syst_fraction=0.05,
    )
    t = est.run(stacked)
    t.write(output)


if __name__ == "__main__":
    main(**vars(args))
