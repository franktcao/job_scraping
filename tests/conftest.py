"""Shared pytest fixtures for Indeed HTML parsing tests."""

import pytest
from bs4 import BeautifulSoup


SAMPLE_ENTRY_HTML = """
<div class="row" data-jk="abc123def456">
  <a data-tn-element="jobTitle" href="/rc/clk?jk=abc123def456">
    Senior Data Scientist
  </a>
  <span class="company">
    Acme Corp
  </span>
  <div class="sjcl">
    <span class="location">Boston, MA 02109<span>(Downtown)</span></span>
  </div>
  <nobr>$100,000 - $150,000 a year</nobr>
  <div class="summary">
    Looking for an experienced data scientist to join our team.
  </div>
</div>
"""

SAMPLE_ENTRY_NO_SALARY_HTML = """
<div class="row" data-jk="xyz789">
  <a data-tn-element="jobTitle" href="/rc/clk?jk=xyz789">
    Junior Data Analyst
  </a>
  <span class="result-link-source">
    Startup Inc
  </span>
  <div class="sjcl">
    <span class="location">Cambridge, MA</span>
  </div>
  <div class="summary">
    Entry-level data analyst position.
  </div>
</div>
"""

SAMPLE_ENTRY_SALARY_SNIPPET_HTML = """
<div class="row" data-jk="sal456">
  <a data-tn-element="jobTitle" href="/rc/clk?jk=sal456">
    ML Engineer
  </a>
  <span class="company">
    BigTech LLC
  </span>
  <div class="sjcl">
    <span class="location">Braintree, MA 02184</span>
  </div>
  <div class="salarySnippet">
    <span class="salary">$120,000 - $180,000 a year</span>
  </div>
  <div class="summary">
    Build production ML systems.
  </div>
</div>
"""


@pytest.fixture
def sample_entry():
    soup = BeautifulSoup(SAMPLE_ENTRY_HTML, 'lxml')
    return soup.find(class_='row')


@pytest.fixture
def sample_entry_no_salary():
    soup = BeautifulSoup(SAMPLE_ENTRY_NO_SALARY_HTML, 'lxml')
    return soup.find(class_='row')


@pytest.fixture
def sample_entry_salary_snippet():
    soup = BeautifulSoup(SAMPLE_ENTRY_SALARY_SNIPPET_HTML, 'lxml')
    return soup.find(class_='row')
