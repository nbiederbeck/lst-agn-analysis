import logging
from pathlib import Path
from . import get_analysis

log = logging.getLogger(__name__)


def main():
    analysis = get_analysis()
    analysis.get_datasets()

    path = Path("build/analysis")
    path.mkdir(exist_ok=True)
    filename = path / "stacked-dataset.fits.gz"

    analysis.datasets["stacked"].write(filename, overwrite=True)

    analysis.read_models("model_config.yaml")

    analysis.run_fit()
    best_fit = "build/model-best-fit.yaml"
    analysis.models.write(best_fit, overwrite=True)
    log.info(f"Fitted model parameters saved to {best_fit}.")


if __name__ == "__main__":
    main()
