# lst-data-selection

Create the authentication file `lst1-authentication.txt` (fill in username and password):
```
<username>:<password>
```

## Usage

To install some local requiremets, run:
```
make install_requirements_with_pip
```

Then edit `config.json` to your liking and run snakemake via make:
```
make
```

### What happens?

1. The most recent run list is downloaded from the LST server.
2. The html-file is converted to a csv-file, only including runs of the configured source.
3. Every DL1 data-check that happens to exist on the server on La Palma
   is listed.
4. All existing data-checks are merged.
5. The merged runs are checked given some cuts written in `scripts/data-check.py`.
   This step generates plots.
6. A file containing the mapping of nights to run IDs is created.

It is possible (and maybe useful) to run steps 1-4 on the cluster,
download the merged file and continue with steps 5-6 on a local machine.
