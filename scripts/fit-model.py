from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-c", "--config", required=True)
parser.add_argument("--dataset-path", required=True)
parser.add_argument("--model-config", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets


def main(config, dataset_path, model_config, output):
    config = AnalysisConfig.read(config)

    analysis = Analysis(config)
    analysis.datasets = Datasets.read(dataset_path)

    analysis.read_models(model_config)

    analysis.run_fit()
    analysis.models.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
