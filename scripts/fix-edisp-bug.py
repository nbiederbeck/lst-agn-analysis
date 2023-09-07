import numpy as np
from astropy.io import fits
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("dl3_file", type=Path)


def main():
    args = parser.parse_args()

    with fits.open(args.dl3_file, "update") as hdul:
        for hdu in hdul:
            if hdu.header.get("HDUCLAS4") != "EDISP_2D":
                continue

            if hdu.header.get("FIXEDNRM"):
                continue

            data = hdu.data[0]
            edisp = data["MATRIX"]
            migra_lo = data["MIGRA_LO"]
            migra_hi = data["MIGRA_HI"]
            width = migra_hi - migra_lo

            normalization = (edisp * width[np.newaxis, :, np.newaxis]).sum(axis=1)

            if np.all(np.isclose(normalization, 1.0, atol=1e-4) | (normalization == 0)):
                print("EDISP is correctly normalized")
                return
            else:
                print("EDISP is incorrectly normalized")


            edisp[:] /= width[np.newaxis, :, np.newaxis]

            hdu.header["FIXEDNRM"] = True, "Normalization of EDISP fixed by script"


if __name__ == "__main__":
    main()
