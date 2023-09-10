from argparse import ArgumentParser

from astropy.time import Time
from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets


def select_timeframe(datasets, t_start, t_stop):
    print(f"Selecting: {t_start}, {t_stop} from")
    print(datasets.gti.time_start)
    print(datasets.gti.time_stop)
    t_start = Time(t_start, format="mjd") if t_start else datasets.gti.time_start[0]
    t_stop = Time(t_stop, format="mjd") if t_stop else datasets.gti.time_stop[-1]
    return datasets.select_time(t_start, t_stop, atol="1e-3 s")


def main(  # noqa: PLR0913
    config,
    dataset_path,
    best_model_path,
    output,
    t_start,
    t_stop,
):
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

    analysis.read_models(best_model_path)

    analysis.get_flux_points()

    analysis.flux_points.write(output, overwrite=True)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", required=True)
    parser.add_argument("--dataset-path", required=True)
    parser.add_argument("--best-model-path", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--t-start", required=False)
    parser.add_argument("--t-stop", required=False)
    args = parser.parse_args()
    main(**vars(args))
