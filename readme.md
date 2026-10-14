# Persian Data Analytics Dashboard

[نسخه‌ی فارسی](readme_fa.md)

A right-to-left Streamlit dashboard for uploading CSV and Excel files, reviewing data quality, applying optional cleaning, filtering records, and building interactive charts.

## Features

- Persian, right-to-left user interface
- CSV, XLSX, and XLS uploads
- Column profiles, missing and duplicate value summaries, and descriptive statistics
- Numeric, date, and categorical filters
- Optional data cleaning and CSV export of processed data
- Interactive charts and a correlation heatmap

## Project structure

| Path | Purpose |
| --- | --- |
| `app.py` | Application entry point and page layout |
| `src/dashboard/data_loader.py` | File validation and loading |
| `src/dashboard/data_profile.py` | Data profiling and cleaning |
| `src/dashboard/filters.py` | Interactive filters |
| `src/dashboard/charts.py` | Chart creation |
| `src/dashboard/exporters.py` | CSV export preparation |
| `src/dashboard/ui_components.py` | Reusable UI components |
| `assets/styles.css` | RTL layout and styling |
| `data/sample_sales.csv` | Public sample data |

## Requirements

- Python 3.14 or later

## Run locally

From the project directory, create a virtual environment and install the dependencies:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

Upload `data/sample_sales.csv` or your own file from the sidebar. Choose filters and cleaning options, then download the processed CSV from the export section.

## Data and privacy

- The dashboard processes files selected by the user. Do not use real or confidential datasets in public demonstrations.
- Uploaded file names are not written to the application log.
- `data/sample_sales.csv` is the public example dataset included with the project.

