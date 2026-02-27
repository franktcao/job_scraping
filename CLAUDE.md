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
├── JobEntry.py                              # HTML parsing helpers for job posting elements
├── scrape_indeed.ipynb                      # Stage 1: Scrape Indeed → raw CSV
├── clean_indeed.ipynb                       # Stage 2: Clean raw CSV → cleaned CSV
├── analyze_indeed.ipynb                     # Stage 3: TF-IDF analysis → tfidf CSV
├── scrathpad_scrape_indeed.ipynb            # Scraping experiments (scratch)
├── scratchpad_bs4_elements.ipynb            # BeautifulSoup selector testing (scratch)
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

Helper class with methods for extracting structured data from BeautifulSoup-parsed Indeed HTML:

| Method | Purpose |
|--------|---------|
| `get_job_title(entry)` | Extract title from `a[data-tn-element='jobTitle']` |
| `get_company(entry)` | Extract company from `span.company` (fallback: `span.result-link-source`) |
| `get_location_info(entry)` | Parse location into city, state, zipcode, neighborhood |
| `get_salary(entry)` | Extract salary from `nobr` or `div.salarySnippet span.salary` |
| `get_link(entry)` | Get job posting ID from `data-jk` attribute |
| `get_job_description(job_page)` | Fetch full description from job detail page |
| `get_job_summary(entry)` | Extract summary from `div.summary` |

**Note:** Methods are defined as instance methods but lack `self` parameter — they function as standalone functions. The class-level import on line 3 (`from requests`) has a syntax error.

## Dependencies

Install manually (no `requirements.txt` exists):

```
pip install pandas requests beautifulsoup4 lxml nltk numpy matplotlib seaborn
```

NLTK data required:
```python
import nltk
nltk.download('punkt')
```

## Configuration

All configuration is hardcoded in notebook cells:

| Parameter | Value | Location |
|-----------|-------|----------|
| `city_set` | `['Boston']` | `scrape_indeed.ipynb` |
| `max_pages_per_city` | `60` | `scrape_indeed.ipynb` |
| `POSTINGS_PER_PAGE` | `17` | `scrape_indeed.ipynb` |
| Rate limit delay | `1 second` | `scrape_indeed.ipynb`, `JobEntry.py` |
| Search query | `"data scientist $20,000"` | `scrape_indeed.ipynb` |
| Salary period multipliers | `{'yearly':1, 'monthly':12, ...}` | `clean_indeed.ipynb` |

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

## Code Conventions

- **Functions/variables:** `snake_case` (e.g., `get_job_title`, `city_set`)
- **Classes:** `PascalCase` (e.g., `JobEntry`)
- **Constants:** `UPPER_CASE` (e.g., `POSTINGS_PER_PAGE`)
- **Imports:** Standard library first, then third-party (`import pandas as pd`, `from bs4 import BeautifulSoup`)
- **Error handling:** Bare `except:` clauses with fallback logic for resilient scraping
- **CSV naming:** `YYYY-MM-DD_indeed-ds-postings[_cleaned|_tfidf].csv`
- **HTML selectors:** CSS class-based selectors via BeautifulSoup's `find()` API

## Known Limitations

- **Stale selectors:** Indeed's HTML structure has changed since 2019; CSS selectors in `JobEntry.py` and notebooks are likely broken against current Indeed pages
- **No dependency management:** No `requirements.txt`, `setup.py`, or `pyproject.toml`
- **No tests:** No test framework; testing is ad-hoc in scratchpad notebooks
- **Hardcoded config:** City list, page limits, and delays are inline in notebook cells
- **JobEntry.py issues:** Methods lack `self` parameter (should be `@staticmethod` or standalone functions); line 3 has a syntax error (`from requests` with no import target)
- **Bare except clauses:** Broad exception handling can mask real errors
- **Low salary coverage:** Only ~6.5% of scraped postings include salary data
- **No CLI interface:** Pipeline can only be run through Jupyter UI
- **Sequential HTTP requests:** No async/parallel fetching; scraping ~1000 pages is slow
- **Manual filename wiring:** Each notebook stage requires manually updating the input CSV filename
