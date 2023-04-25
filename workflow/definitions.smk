# vim: ft=snakemake nofoldenable commentstring=#%s
# https://github.com/snakemake/snakemake/tree/main/misc/vim
import json
from itertools import chain
from pathlib import Path

with open("../lst-analysis-config/lst_agn.json", "r") as f:
    config_agn = json.load(f)

with open("build/runs.json", "r") as f:
    runs = json.load(f)

gammapy_env = "envs/agn-analysis.yml"
lstchain_env = config_agn.get("lstchain_enviroment", "lstchain-v0.9.13")

PRODUCTION = config_agn["production"]
DECLINATION = config_agn["declination"]
RUN_IDS = sorted(set(chain(*runs.values())))

irf_plots = [
    f"build/plots/irf/{irf}_Run{run_id:05d}.pdf"
    for irf in ("aeff", "edisp", "gh_cut", "radmax_cut")
    for run_id in RUN_IDS
]

analyses = [
    x.name
    for x in Path("../lst-analysis-config").iterdir()
    if x.name.startswith("analysis") and x.is_dir()
]

dl3_plots = [
    f"build/plots/{plot}/{run:05d}.pdf" for run in RUN_IDS for plot in ["theta2"]
] + ["build/plots/theta2/stacked.pdf"]


# observation plots are arguably dl3
dl4_plots = [
    f"build/plots/{analysis}/{plot}.pdf"
    for analysis in analyses
    for plot in ["light_curve", "flux_points", "observation_plots"]
]
