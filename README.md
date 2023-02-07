# lst-data-selection

Create the authentication file `lst1-authentication.json` (fill in username and password):
```json
{
    "auth": {
        "raw_auth": "<username>:<password>",
        "type": "basic"
    }
}
```

## Usage
Provide a known source when running make:
```
SOURCE=Crab make
```

### What happens?

1. The most recent run list is downloaded from the LST server.
2. The html-file is converted to a csv-file, only including runs of the provided `SOURCE`.
3. Every DL1 data-check that happens to exist on the server on La Palma
   is listed.
4. All existing data-checks are archived.
5. The archive is unpacked.
6. The runs are checked given some cuts written in `scripts/data-check.py`.
   This step generates plots.
7. A file containing the mapping of nights to run IDs is created.

It is possible (and maybe useful) to run steps 1-4 on the cluster,
download the archive and continue with steps 5-7 on a local machine.
