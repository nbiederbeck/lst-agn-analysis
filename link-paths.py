from pathlib import Path

import numpy as np
import tables
from tqdm import tqdm

from run_ids import mrk421, one_es1959

sources = {
    "mrk421": mrk421,
    "one_es1959": one_es1959,
}

outdir = "build/dl1/{source}/{zd}/"
filename = "dl1_LST-1.Run{run_id:05d}.h5"
template_target = "/fefs/aswg/data/real/DL1/{night}/v0.9/tailcut84/" + filename
template_linkname = outdir + filename


if __name__ == "__main__":
    for name, source in tqdm(sources.items()):
        for night, run_ids in tqdm(source.items(), position=1):
            for run_id in tqdm(run_ids, position=2):
                target = template_target.format(night=night, run_id=run_id)

                # check mean zenith distance
                with tables.open_file(
                    target,
                    root_uep="/dl1/event/telescope/parameters",
                    mode="r",
                ) as f:
                    zd_mean = 90 - np.rad2deg(
                        f.get_node("/LST_LSTCam").col("alt_tel").mean()
                    )

                if zd_mean < 30:
                    zd = "zenith_20deg"
                else:
                    zd = "zenith_40deg"

                linkname = Path(
                    template_linkname.format(
                        night=night,
                        run_id=run_id,
                        zd=zd,
                        source=name,
                    )
                )

                if not linkname.is_file():
                    linkname.parent.mkdir(exist_ok=True, parents=True)
                    linkname.symlink_to(target)
