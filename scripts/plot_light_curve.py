from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--input-path", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()


from gammapy.estimators import FluxPoints
from matplotlib import pyplot as plt


def main(input_path, output):
    lc = FluxPoints.read(input_path, format="lightcurve")

    fig, ax = plt.subplots()
    lc.plot(ax=ax)
    fig.savefig(output)


if __name__ == "__main__":
    main(**vars(args))
