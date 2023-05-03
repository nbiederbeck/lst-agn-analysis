from argparse import ArgumentParser

from gammapy.maps import WcsMap

parser = ArgumentParser()
parser.add_argument("-i", "--input-paths", required=True, nargs="+")
parser.add_argument("-o", "--output-path", required=True)
args = parser.parse_args()


def main(input_paths, output_path):
    skymap = WcsMap.read(input_paths[0], map_type="wcs")

    for path in input_paths[1:]:
        sky_map = WcsMap.read(path, map_type="wcs")
        skymap.data += sky_map.data

    skymap.write(output_path, overwrite=True)


if __name__ == "__main__":
    main(**vars(args))
