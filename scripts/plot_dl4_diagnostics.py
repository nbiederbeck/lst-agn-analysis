from argparse import ArgumentParser

import matplotlib
from astropy.io import fits
from astropy.table import Table
from matplotlib import pyplot as plt

if matplotlib.get_backend() == "pgf":
    from matplotlib.backends.backend_pgf import PdfPages
else:
    from matplotlib.backends.backend_pdf import PdfPages


parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


def main(input_path, output):
    figures = []
    with fits.open(input_path) as f:
        # Skip primary
        for hdu in f[1:]:
            table = Table.read(hdu)
            y_cols = ["excess", "sqrt_ts"]
            x_cols = set(table.columns).difference(y_cols)
            for y in y_cols:
                for x in x_cols:
                    fig, ax = plt.subplots()
                    ax.scatter(table[x], table[y])
                    # TODO These are not super nice
                    ax.set_xlabel(x)
                    ax.set_ylabel(y)
                    if table.meta["CUMUL"]:
                        ax.set_title(f"Cumulative {y}")
                    figures.append(fig)

    if output is None:
        plt.show()
    else:
        with PdfPages(output) as pdf:
            for fig in figures:
                pdf.savefig(fig)


if __name__ == "__main__":
    main(**vars(args))
