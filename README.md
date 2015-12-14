# gvaparse
Requirements: SQLite3 in the directory

A script to parse and store into an SQLite table web scraped data.

Use:
---
parser.py converts the scraped HTML blocks into a SQLite database.

puller.py queries the SQLite database and generate csv files for use in webpages.

To be used interactively:
---
datafilter.py queries the SQLite database and is used for drawing graphs.

model.py queries the SQLite database and is intended for use alongside `scikit-learn`
