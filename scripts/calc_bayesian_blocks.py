from argparse import ArgumentParser

from astropy.stats import bayesian_blocks
from astropy.table import Table
from gammapy.estimators import FluxPoints

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("--threshold", default=0.0027, type=float)
args = parser.parse_args()


def main(input_path, output, threshold):
    lc = FluxPoints.read(input_path, format="lightcurve")
    table = lc.to_table(format="lightcurve", sed_type="flux")

    # No error on t
    t_min = table["time_min"]
    t_max = table["time_max"]
    t = (t_min + t_max) / 2

    # x is the measured quantity, sigma its uncertainty
    x = table["flux"].flatten()
    sigma = table["flux_err"].flatten()

    blocks = bayesian_blocks(t=t, x=x, p0=threshold, fitness="measures", sigma=sigma)

    t = Table()
    t["start"] = blocks[:-1]
    t["stop"] = blocks[1:]
    t.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
