# lst-data-selection

Download the LST Source Catalog (runlist), replace `<username>` and `<password>`:

```
curl --user <username>:<password> \
    https://lst1.iac.es/datacheck/lstosa/LST_source_catalog.html \
    -o runlist.html
```

## Usage

To install some local requirements, run:

```
make install_requirements_with_pip
```

Then edit `config.json` to your liking and run snakemake via make:

```
make
```
