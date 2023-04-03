# lst-data-selection

Download the LST Source Catalog (runlist), replace `<username>` and `<password>`:

```
curl --user <username>:<password> \
    https://lst1.iac.es/datacheck/lstosa/LST_source_catalog.html \
    -o runlist.html
```

## Usage

To install some local requirements, create the enviroment using conda/mamba:

```
mamba env create -f workflow/environment.yml
mamba activate lst-data-selection
```

Then edit `config.json` to your liking and run snakemake via make:

```
make
```

## Local Usage

If you have run snakemake on the cluster, you can create the plots and tex files locally.
First, you need to download `build/dl1-datacheck-masked.h5`, e.g.:

```
mkdir -p build
scp <host>:<path-to>/lst-data-selection/build/dl1-datachecks-masked.h5 build/
```

Afterwards:

```
make -f local.mk
```
