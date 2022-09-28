import logging
from pathlib import Path

from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.datasets import Datasets

log = logging.getLogger(__name__)


def main():
    config = AnalysisConfig.read("configs/config.yaml")

    analysis = Analysis(config)
    analysis.datasets = Datasets.read("build/datasets.fits.gz")

    analysis.read_models("configs/model_config.yaml")

    analysis.run_fit()
    best_fit = "build/model-best-fit.yaml"
    analysis.models.write(best_fit, overwrite=True)
    log.info(f"Fitted model parameters saved to {best_fit}.")


if __name__ == "__main__":
    main()
