# Oraclr

This project relies on Google Alerts to continuously build a database of research around the articles reported by Google Alerts. This app uses the Gmail API to read Google Alerts emails, extract article links, fetch content, and generate CSV reports with structured data.

## Features

- Fetch Google Alerts emails from Gmail using the Gmail API
- Parse alerts to extract article URLs and topics
- Optionally fetch article content for executive summaries
- Generate CSV reports with fields:
  - Date
  - Time
  - URL link
  - Topic
  - Executive summary
  - Reference links

## Quick Start

### 1. Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) — install with `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- A Google Cloud project with Gmail API enabled
- OAuth 2.0 credentials (credentials.json)

### 2. Set up Google Cloud credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API for your project
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the credentials and save as `credentials.json` in your project directory

### 3. Install Oraclr

```bash
# Clone or navigate to the project directory
cd oraclr

# Create .venv, install Python 3.12 if needed, and install dependencies from uv.lock
uv sync
```

`uv sync` is optional: `uv run` creates and syncs the environment automatically on first use.

### 4. Run Oraclr

```bash
# Fetch Google Alerts and generate CSV (basic)
uv run oraclr fetch

# Fetch with article content (takes longer)
uv run oraclr fetch --fetch-content

# Fetch more emails
uv run oraclr fetch --max-results 50

# Specify custom output directory
uv run oraclr fetch --output-dir my_reports

# Test parsing a single URL
uv run oraclr parse-url https://example.com/article
```

### 5. First Run

On the first run, you'll be prompted to:
1. Authorize the application in your browser
2. Allow access to read your Gmail
3. The authorization token will be saved in `token.json` for future use

### 6. Output

CSV files will be generated in the `output/` directory (or your specified directory) with the format:
```
google_alerts_YYYYMMDD_HHMMSS.csv
```

## Example CSV Output

```csv
date,time,url,topic,executive_summary,reference_links
2025-10-05,14:30:00,https://example.com/article1,AI News,This article discusses...,https://ref1.com; https://ref2.com
2025-10-05,14:30:00,https://example.com/article2,Tech Update,New developments in...,https://ref3.com
```

## Project Structure

```
oraclr/
├── src/
│   └── oraclr/
│       ├── __init__.py
│       ├── gmail_client.py    # Gmail API interaction
│       ├── alert_parser.py    # Parse Google Alerts
│       ├── csv_generator.py   # Generate CSV files
│       └── cli.py             # Command-line interface
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependency versions (commit this)
├── .python-version        # Python version used by uv
├── README.md
└── credentials.json           # (You need to create this)
```

## Development

Development tools (pytest, black, flake8) are in the `dev` dependency group, which `uv sync` installs by default.

```bash
uv run pytest            # Run tests
uv run black src         # Format code
uv run flake8 src        # Lint code

uv add <package>         # Add a dependency (updates pyproject.toml and uv.lock)
uv add --dev <package>   # Add a development dependency
uv lock --upgrade        # Upgrade locked dependency versions
```

## Troubleshooting

- **No emails found**: Make sure you have Google Alerts set up to send to your Gmail
- **Authentication errors**: Delete `token.json` and run again to re-authenticate
- **API quota exceeded**: Google has daily API limits; try reducing `--max-results`


