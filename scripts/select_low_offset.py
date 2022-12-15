from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--input-file", required=True)
parser.add_argument("-o", "--output", required=True)
args = parser.parse_args()

from astropy import units as u
from gammapy.data import Observation


def main(input_file, output):
    obs = Observation.read(input_file).copy()
    mask = obs.events.offset.to_value(u.deg) < 1
    obs._events.table = obs.events.table[mask]
    obs.write(output, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
