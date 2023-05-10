from argparse import ArgumentParser

from calc_flux_points import select_timeframe
from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("--dataset-path", required=True)
parser.add_argument("--model-config", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("--t-start", required=False)
parser.add_argument("--t-stop", required=False)
args = parser.parse_args()


def main(config, dataset_path, model_config, output, t_start, t_stop):  # noqa: PLR0913
    config = AnalysisConfig.read(config)

    analysis = Analysis(config)
    datasets = Datasets.read(dataset_path)
    # Since we read the datasets here, they need not to be stacked
    # Especially our helper script to handle energy-dependent theta-cuts
    # does not stack at all.
    # This is helpful to still have per-run information, but means
    # we need to explicitly stack here, which should be cheap

    # Also if they are not stacked, we can select the ones we want here:
    datasets = select_timeframe(datasets, t_start, t_stop)

    if config.datasets.stack:
        analysis.datasets = Datasets([datasets.stack_reduce()])
    else:
        analysis.datasets = datasets

    analysis.read_models(model_config)

    analysis.run_fit()
    analysis.models.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
