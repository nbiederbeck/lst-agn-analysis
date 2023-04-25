# vim: ft=snakemake nofoldenable commentstring=#%s
# https://github.com/snakemake/snakemake/tree/main/misc/vim
import json
from pathlib import Path

gammapy_env = Path("workflow/envs/agn-analysis.yml").resolve()
data_selection_env = Path("workflow/envs/data-selection.yml").resolve()

config_dir = Path("../lst-analysis-config")
irf_config_path = (config_dir / "irf_tool_config.json").resolve()
data_selection_config_path = (config_dir / "data-selection.json").resolve()
main_config_path = (config_dir / "lst_agn.json").resolve()

with open(main_config_path, "r") as f:
    config_agn = json.load(f)

PRODUCTION = config_agn["production"]
DECLINATION = config_agn["declination"]
lstchain_env = config_agn.get("lstchain_enviroment", "lstchain-v0.9.13")
