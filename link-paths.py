from pathlib import Path

import numpy as np
import tables

from run_ids import mrk421

outdir = "build/dl1/{zd}/"
filename = "dl1_LST-1.Run{run_id:05d}.h5"
template_target = "/fefs/aswg/data/real/DL1/{night}/v0.9/tailcut84/" + filename
template_linkname = outdir + filename

Path(outdir).mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    for night, run_ids in mrk421.items():
        for run_id in run_ids:
            target = template_target.format(night=night, run_id=run_id)

            # check mean zenith distance
            with tables.open_file(
                target, root_uep="/dl1/event/telescope/parameters"
            ) as f:
                zd_mean = 90 - np.rad2deg(np.mean(f.root.LST_LSTCam.col("alt_tel")))

            print(zd_mean)

            if zd_mean < 30:
                zd = "low"
            else:
                zd = "high"

            linkname = template_linkname.format(night=night, run_id=run_id, zd=zd)

            Path(linkname).symlink_to(target)
