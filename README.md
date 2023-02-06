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
