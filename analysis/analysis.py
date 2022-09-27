import logging
from pathlib import Path
from gammapy.analysis import Analysis, AnalysisConfig

log = logging.getLogger(__name__)


def main():
    config = AnalysisConfig.read("configs/config.yaml")

    analysis = Analysis(config)
    analysis.get_observations()

    analysis.get_datasets()

    path = Path("build/analysis")
    path.mkdir(exist_ok=True)
    filename = path / "stacked-dataset.fits.gz"

    analysis.datasets["stacked"].write(filename, overwrite=True)

    analysis.read_models("configs/model_config.yaml")

    analysis.run_fit()
    best_fit = "build/model-best-fit.yaml"
    analysis.models.write(best_fit, overwrite=True)
    log.info(f"Fitted model parameters saved to {best_fit}.")


if __name__ == "__main__":
    main()
