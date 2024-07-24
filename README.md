# starchaser
Scrape and aggregate UKC logbook data and display in Streamlit.

## View the dashboard
[Reach for the stars!](https://starchaser.minchus.com)

## Development
### Environment setup
Prerequisites:
 - hatch
 - python > 3.8 (will be installed by hatch)

### Run local Streamlit dashboard
The local Streamlit app will read secrets from a file .streamlit/secrets.toml in the repo's root directory.
Create this file if it doesn't exist yet and add the share link of your Google Sheet to it as shown below:
```
# .streamlit/secrets.toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/xxxxxxx/edit#gid=0"
```
Then run:

```hatch run streamlit run ./src/starchaser/Explore_Crags.py```

### Run scrape
```hatch run scrape```

By default, the data directory for the request cache and output CSV is `./data/`
which will be created if it does not exist.

### Run tests
```hatch run test```
