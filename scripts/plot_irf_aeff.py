from argparse import ArgumentParser

from gammapy.irf import load_irf_dict_from_file
from matplotlib import pyplot as plt

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(input_path, output):
    aeff = load_irf_dict_from_file(input_path)["aeff"]

    e_true = aeff.axes["energy_true"]

    offset = aeff.axes["offset"]
    unit = offset.unit
    label = r" \pm ".join(
        [
            f"${offset.center.to_value(unit)[0]}",
            f"{offset.bin_width.to_value(unit)[0] / 2:.1f}$ {unit}",
        ]
    )

    fig, ax = plt.subplots()

    ax.errorbar(
        e_true.center,
        aeff.data,
        xerr=e_true.bin_width / 2,
        ls="",
        label=f"Offset: {label}",
        color="black",
    )
    ax.set_xlabel(rf"$E_{{\mathrm{{true}}}}$ / {e_true.center.unit}")
    ax.set_ylabel(f"Effective Area / {aeff.unit}")

    ax.set_xscale("log")
    ax.set_yscale("log")

    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
