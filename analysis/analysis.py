from pathlib import Path
from . import get_analysis


def main():
    analysis = get_analysis()
    analysis.get_datasets()

    path = Path("build/analysis")
    path.mkdir(exist_ok=True)
    filename = path / "stacked-dataset.fits.gz"

    analysis.datasets["stacked"].write(filename, overwrite=True)

    analysis.read_models("model_config.yaml")

    analysis.run_fit()
    analysis.models.write("build/model-best-fit.yaml", overwrite=True)


if __name__ == "__main__":
    main()
