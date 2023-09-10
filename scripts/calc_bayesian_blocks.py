from argparse import ArgumentParser
import numpy as np
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
    # TODO This only works with the hardcoded systematic and edge shift

    # No error on t
    t_min = table["time_min"]
    t_max = table["time_max"]
    t = (t_min + t_max) / 2

    # x is the measured quantity, sigma its uncertainty
    x = table["flux"].flatten()
    # Add the systematic uncertainty.
    sigma = np.sqrt(table["flux_err"].flatten() ** 2 + (0.08 * x)**2)

    blocks = bayesian_blocks(t=t, x=x, p0=threshold, fitness="measures", sigma=sigma)

    t = Table()
    # The blocks refer to the time of the flux points
    # That is the middle of the run/night depending on how thats calculated
    # Right now we only calculate the runwise nightcurve here
    # Thats something that should maybe be changed. 
    # Then we also need to adapt the shifts here 

    # 20 min in mjd
    shift = 1 / 24 / 3
    t["start"] = blocks[:-1] - shift
    t["stop"] = blocks[1:] + shift
    t.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
