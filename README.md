# LST AGN Analysis

This project tries to handle all the steps needed for a typical AGN-analysis (or any point-source really):

- Select runs observing the source and matching some quality criteria
- Apply models on dl1 files / Produce dl2
- Calculate IRFs
- Produce dl3
- Run the gammapy data reduction to dl4
- Perform spectral fit, calculate flux points, calculate light-curve, ...
- Perform multiple gammapy analyses with the same dl3

What it does NOT handle:

- Low-level calibrations. We start at DL1
- Non standard MC. We use the standard all-sky
- Perform a 3D analysis
- Perform any "non-standard" high-level analysis (pulsars etc)

Conceptually there are three main steps (You could define more, but these are still somewhat split in the workflow):

- Select runs via the datacheck files
- Link runs and mc to the `build` directory. This makes rules easier to reason about. These are only links, not copies (!) and show up as such using `ls -l`.
- Run the analysis using `lstchain` and `gammapy`

# Usage

## Prerequisites

You need snakemake installed. If you do not have that, you can create an enviroment with only snakemake like this:

```
mamba env create -f workflow/envs/snakemake.yml
mamba activate snakemake
```

For development, you should also install atleast pre-commit.
The enviroment in `workflow/envs/data-selection` should contain everything (Don't forget to `pre-commit install` afterwards).
This is not a specific development enviroment though.
Cleaning up the envs is definetively a TODO as it got a bit messy after merging what was originally two projects.

Also you need the source catalogue. Since this requires credentials (standard LST ones), it is not done automatically.
This is needed only once (or whenever you want to use new runs).
You can use this command (replace `<username>` and `<password>`):

```
curl --user <username>:<password> \
    https://lst1.iac.es/datacheck/lstosa/LST_source_catalog.html \
    -o runlist.html
```

## Config

Adapt to your liking

- Data selection: `config.json` (TODO: Move this)
- MCs to use, lstchain env and number of off regions: `configs/slt_agn.json` (gammapy does not handle energy-dependent cuts automatically, so we need to work around this)
- IRFs (lstchain): `configs/irf_tool_config.json`
- gammapy: `analysis.yaml` and `models.yaml` in subdirectories `configs/analysis_*`. All `analysis*` directories will be searched, so you might want to remove the standard ones first (TODO: Find a better solution for this). These all use the same dl3, but produce their own dl4

## Run the analysis

Basically only run `make`.
If you run it without a specific target, everything should be resolved.
In the event, that you give a target such as `make build/plots/analysis-one/flux_points.pdf`, the linking part might not run again.
This is clearly suboptimal, but for now you will need to run `make link` first IF YOU CHANGED SOMETHING in the data selection.
Since in this case, one probably wants to rerun everything anyway, this was not super high on our priority.
It is related to https://github.com/nbiederbeck/lst-agn-analysis/issues/26

## Local Usage

If you have run snakemake on the cluster, you can create the plots and tex files locally (using your own matplotlibrc for example).
We separate the calculation of metrics and the plotting to make sure you can finetune plots later on without needing to
run the expensive steps on the local machine. The tables for that are saved as either `fits.gz` or `h5`.

For the data-selection plots, you need to download `build/dl1-datacheck-masked.h5`, e.g.:

```
mkdir -p build
scp <host>:<path-to>/lst-data-selection/build/dl1-datachecks-masked.h5 build/
```

Afterwards:

```
make -f local.mk
```

TODO: Do the same for the other plots (https://github.com/nbiederbeck/lst-agn-analysis/issues/39)
If you do some `cp **/*.fits.gz` shenanigans, beware that the dl3 files are saved as with
the extension `fits.gz` as well.
