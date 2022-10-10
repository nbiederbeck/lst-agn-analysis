from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("--dataset-path", required=True)
parser.add_argument("--best-model-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets


def main(config, dataset_path, best_model_path, output):
    config = AnalysisConfig.read(config)

    analysis = Analysis(config)

    analysis.datasets = Datasets.read(dataset_path)

    analysis.read_models(best_model_path)

    analysis.get_flux_points()

    analysis.flux_points.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
