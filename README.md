# SSL/TLS Certificate Expiry Checker

A Streamlit‑based web application to monitor and visualize SSL/TLS certificate expiration for one or more hosts. Ideal for sysadmins and devops teams to proactively detect expiring or expired certificates.

## Features

- Batch host checks via text input or file upload

- Concurrent execution using a thread pool for fast scanning

- Custom warning threshold (e.g. flag certs expiring in ≤ 15 days)

- Interactive dashboard:
  - Summary metrics: total, OK, warnings, errors

  - Bucketed bar chart (expired, 0–7 days, 8–30 days, etc.)

  - Detailed results table with row highlighting for warnings/errors

  - Data export: Download CSV or JSON of results

  - Caching: Results are cached to avoid redundant checks

## Installation

1. Clone the repository
```
git clone https://github.com/your‑org/ssl‑expiry‑checker.git
cd ssl‑expiry‑checker
```

2. Create and activate a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate    # Linux/macOS
.\.venv\Scripts\activate   # Windows
```

3. Install dependencies
```
pip install -r requirements.txt
```

## Configuration & Usage

1. Run the Streamlit app
```
streamlit run ssl_expiry_streamlit.py
```

2. Configure settings in the sidebar:

- Hosts: Paste hostnames (one per line) or upload a .txt file

- Port: Default is 443

- Warn if expiring in ≤ days: Set your threshold (e.g. 15)

- Concurrency: Number of threads for parallel checks

3. Click the Check Certificates button.

4. View results:

- Summary metrics at the top

- Expiry buckets bar chart

- Expandable table with detailed data and download options

## Dependencies

- Streamlit — Fast web apps in Python

- Pandas — Data manipulation

- Altair — Declarative charts

## Development

- Code style: PEP8

- Formatting: Use black . and isort .

- Testing: Extend with pytest for unit tests on certificate parsing and data processing

## Deployment

- Run locally via streamlit run

- Docker: create a Dockerfile and expose port 8501

- Streamlit Cloud: connect your GitHub repo for one‑click deployment

## Contributing

Contributions are welcome! Please:

1. Fork the repo

2. Create a feature branch: git checkout -b feat/YourFeature

3. Commit your changes: `git commit -m "Add feature"

4. Push branch: git push origin feat/YourFeature

5. Open a pull request

## License
This project is licensed under the MIT License.
