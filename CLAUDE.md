# CLAUDE.md

## Project Overview

Indeed.com job scraping and analysis project for data scientist postings. The project implements a three-stage pipeline:

1. **Scrape** — Extract job postings from Indeed using `requests` + `BeautifulSoup`
2. **Clean** — Deduplicate, normalize salaries/locations, standardize schema
3. **Analyze** — Compute TF-IDF keyword importance scores across job descriptions

**Tech stack:** Python, Jupyter Notebooks, BeautifulSoup4, pandas, NLTK, matplotlib/seaborn

## Repository Structure

```
job_scraping/
├── JobEntry.py                              # Standalone HTML parsing functions for job posting elements
├── config.yaml                              # Centralized scraping/cleaning configuration
├── requirements.txt                         # Python dependencies
├── scrape_indeed.ipynb                      # Stage 1: Scrape Indeed → raw CSV
├── clean_indeed.ipynb                       # Stage 2: Clean raw CSV → cleaned CSV
├── analyze_indeed.ipynb                     # Stage 3: TF-IDF analysis → tfidf CSV
├── scrathpad_scrape_indeed.ipynb            # Scraping experiments (scratch)
├── scratchpad_bs4_elements.ipynb            # BeautifulSoup selector testing (scratch)
├── tests/                                   # pytest test suite
│   ├── __init__.py
│   ├── conftest.py                          # Shared HTML fixtures for tests
│   └── test_job_entry.py                    # Tests for JobEntry parsing functions
├── 2019-09-02_indeed-ds-postings.csv        # Raw scrape data (Sept 2)
├── 2019-09-02_indeed-ds-postings_cleaned.csv
├── 2019-09-02indeed_ds_postings.csv         # Alternate naming of Sept 2 raw data
├── 2019-09-03_indeed-ds-postings.csv        # Raw scrape data (Sept 3, 1007 rows)
├── 2019-09-03_indeed-ds-postings_cleaned.csv # Cleaned data (461 rows)
├── 2019-09-03 indeed-ds-postings_tfidf.csv  # TF-IDF output (462 rows)
├── test.csv                                 # Small test dataset (179 rows)
└── texput.log                               # LaTeX compilation artifact
```

## Data Pipeline

### Stage 1: Scraping (`scrape_indeed.ipynb`)

- Searches Indeed for "data scientist $20,000+" in configurable cities (default: Boston)
- Iterates up to 60 pages per city (~17 postings/page)
- Fetches full job descriptions from individual job detail pages
- 1-second delay between requests for rate limiting
- **Output:** `YYYY-MM-DD_indeed-ds-postings.csv`
- **Columns:** job_title, company_name, location, neighborhood, description, salary, link

### Stage 2: Cleaning (`clean_indeed.ipynb`)

- Removes duplicate postings (~50% reduction)
- Parses and normalizes salary to annual equivalent using conversion factors:
  - yearly: 1x, monthly: 12x, weekly: 52x, daily: 261x, hourly: 2088x
- Splits location into city, state, zipcode, neighborhood
- Lowercases descriptions for NLP consistency
- **Input:** raw CSV from Stage 1
- **Output:** `YYYY-MM-DD_indeed-ds-postings_cleaned.csv`
- **Columns:** job_title, company_name, annual_salary, city, state, zipcode, neighborhood, description, link

### Stage 3: Analysis (`analyze_indeed.ipynb`)

- Tokenizes descriptions using NLTK `word_tokenize`
- Computes term frequency with log normalization: `1 + log(1 + count)`
- Computes inverse document frequency: `log(1 / (doc_count / (n_posts - doc_count + 1)))`
- Generates per-posting TF-IDF scores
- **Input:** cleaned CSV from Stage 2
- **Output:** `YYYY-MM-DD indeed-ds-postings_tfidf.csv`
- **Additional columns:** term_counts (dict), tfidf (OrderedDict)

## Key File: JobEntry.py

Standalone functions for extracting structured data from BeautifulSoup-parsed Indeed HTML:

| Function | Purpose |
|----------|---------|
| `get_job_title(entry)` | Extract title from `a[data-tn-element='jobTitle']` |
| `get_company(entry)` | Extract company from `span.company` (fallback: `span.result-link-source`) |
| `get_location_info(entry)` | Parse location into city, state, zipcode, neighborhood |
| `get_salary(entry)` | Extract salary from `nobr` or `div.salarySnippet span.salary` |
| `get_link(entry)` | Get job posting ID from `data-jk` attribute |
| `get_job_description(job_page)` | Fetch full description from job detail page |
| `get_job_summary(entry)` | Extract summary from `div.summary` |

Exception handling uses specific `AttributeError` catches with fallback logic for resilient scraping.

## Dependencies

Install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

NLTK data required:
```python
import nltk
nltk.download('punkt')
```

## Configuration

Scraping and cleaning parameters are defined in `config.yaml`:

| Parameter | Value | Config Key |
|-----------|-------|------------|
| Cities | `['Boston']` | `scraping.cities` |
| Max pages per city | `60` | `scraping.max_pages_per_city` |
| Postings per page | `17` | `scraping.postings_per_page` |
| Rate limit delay | `1 second` | `scraping.request_delay_seconds` |
| Search query | `"data scientist $20,000"` | `scraping.search_query` |
| Salary period multipliers | `yearly: 1, monthly: 12, ...` | `cleaning.salary_period_multipliers` |

**Note:** The notebooks still contain hardcoded values and have not yet been updated to read from `config.yaml`. The config file serves as the canonical source of truth for these parameters.

## Running the Project

Execute notebooks sequentially in order:

```bash
# 1. Scrape (produces raw CSV)
jupyter notebook scrape_indeed.ipynb
# Run all cells — output: YYYY-MM-DD_indeed-ds-postings.csv

# 2. Clean (produces cleaned CSV)
jupyter notebook clean_indeed.ipynb
# Update input filename to match Step 1 output, run all cells

# 3. Analyze (produces TF-IDF CSV)
jupyter notebook analyze_indeed.ipynb
# Update input filename to match Step 2 output, run all cells
```

Each notebook requires manually updating the input CSV filename to match the previous stage's output.

## Testing

Run the test suite with pytest:

```bash
python -m pytest tests/ -v
```

Tests cover all `JobEntry.py` parsing functions using HTML fixtures that simulate Indeed's page structure. Fixtures are defined in `tests/conftest.py` with three variants:
- `sample_entry` — Full entry with salary in `<nobr>` tag
- `sample_entry_no_salary` — Entry without salary, company via fallback selector
- `sample_entry_salary_snippet` — Entry with salary in `div.salarySnippet`

## Code Conventions

- **Functions/variables:** `snake_case` (e.g., `get_job_title`, `city_set`)
- **Classes:** `PascalCase` (e.g., `JobEntry`)
- **Constants:** `UPPER_CASE` (e.g., `POSTINGS_PER_PAGE`)
- **Imports:** Standard library first, then third-party (`import pandas as pd`, `from bs4 import BeautifulSoup`)
- **Error handling:** Specific exception types (e.g., `AttributeError`) with fallback logic
- **CSV naming:** `YYYY-MM-DD_indeed-ds-postings[_cleaned|_tfidf].csv`
- **HTML selectors:** CSS class-based selectors via BeautifulSoup's `find()` API
- **Tests:** pytest with class-based test grouping and shared fixtures in `conftest.py`

## Known Limitations

- **Stale selectors:** Indeed's HTML structure has changed since 2019; CSS selectors in `JobEntry.py` and notebooks are likely broken against current Indeed pages
- **Notebooks not wired to config.yaml:** The notebooks still use inline hardcoded values; `config.yaml` exists as a reference but is not yet loaded by the notebooks
- **Low salary coverage:** Only ~6.5% of scraped postings include salary data
- **No CLI interface:** Pipeline can only be run through Jupyter UI
- **Sequential HTTP requests:** No async/parallel fetching; scraping ~1000 pages is slow
- **Manual filename wiring:** Each notebook stage requires manually updating the input CSV filename
- **Bare except clauses in notebooks:** `scrape_indeed.ipynb` and `clean_indeed.ipynb` still use broad `except:` clauses (fixed in `JobEntry.py`)
