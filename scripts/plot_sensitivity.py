from argparse import ArgumentParser

import matplotlib.pyplot as plt
from astropy.table import Table
from gammapy.modeling.models import create_crab_spectral_model

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(input_path, output):
    t = Table.read(input_path)

    fig, ax = plt.subplots()

    ax.plot(
        t["energy"][t["criterion"] == "significance"],
        t["e2dnde"][t["criterion"] == "significance"],
        "s",
        label="significance",
    )
    ax.plot(
        t["energy"][t["criterion"] == "gamma"],
        t["e2dnde"][t["criterion"] == "gamma"],
        "*",
        label="gamma",
    )
    ax.plot(
        t["energy"][t["criterion"] == "bkg"],
        t["e2dnde"][t["criterion"] == "bkg"],
        "v",
        label="bkg syst",
    )
    elim = min(t["energy"].quantity), max(t["energy"].quantity)

    crab = create_crab_spectral_model()
    for n in (1, 0.1, 0.01):
        crab.norm.scale = n
        # TODO It would be nicer to have the label next to the line
        # and not in the legend
        # Then everything could be light gray
        crab.plot(
            elim,
            ax=ax,
            sed_type="e2dnde",
            label=f"{n:.0%} Crab",
            linestyle="dashed",
            alpha=0.3,
        )

    ax.loglog()
    ax.set_xlabel(f"Energy ({t['energy'].unit})")
    ax.set_ylabel(f"Sensitivity ({t['e2dnde'].unit})")
    ax.legend()
    ax.set_ylim(2e-14, 2e-10)

    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
