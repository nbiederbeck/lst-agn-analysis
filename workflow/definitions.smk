import json
from pathlib import Path

config_dir = Path(config.get("config_dir", "../lst-analysis-config"))
build_dir = Path("build") / config_dir.name
env_dir = Path("workflow/envs")

# .resolve(), because I am paranoid
main_config_path = (config_dir / "lst_agn.json").resolve()
data_selection_config_path = (config_dir / "data-selection.json").resolve()
irf_config_path = (config_dir / "irf_tool_config.json").resolve()

with open(main_config_path, "r") as f:
    config_agn = json.load(f)

PRODUCTION = config_agn["production"]
DECLINATION = config_agn["declination"]

lstchain_env = config_agn.get("lstchain_enviroment", "lstchain-v0.9.13")
gammapy_env = (env_dir / "agn-analysis.yml").resolve()
data_selection_env = (env_dir / "data-selection.yml").resolve()

bayesian_block_threshold = config_agn.get("bayesian_block_threshold", 0.0027)
