# starchaser
 Reach for the stars

## View the dashboard
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://<your-custom-subdomain>.streamlit.app)

## Development
### Environment setup
Prerequisites:
 - system python > 3.8
 - hatch

### Run local Streamlit dashboard
The local Streamlit app will read secrets from a file .streamlit/secrets.toml in the repo's root directory.
Create this file if it doesn't exist yet and add the share link of your Google Sheet to it as shown below:
```
# .streamlit/secrets.toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/xxxxxxx/edit#gid=0"
```
Then run:

```hatch run streamlit run ./src/starchaser/main.py```

### Run scrape
```hatch run scrape```

By default data directory for the request cache and output CSV is `./data/`
which will be created if it does not exist.

### Run tests
```hatch run test```