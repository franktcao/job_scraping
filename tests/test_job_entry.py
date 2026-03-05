"""Tests for JobEntry parsing class."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from JobEntry import JobEntry


class TestJobTitle:
    def test_extracts_title(self, sample_entry):
        job = JobEntry(sample_entry)
        assert job.job_title == 'Senior Data Scientist'

    def test_strips_whitespace(self, sample_entry):
        job = JobEntry(sample_entry)
        assert job.job_title == job.job_title.strip()


class TestCompany:
    def test_extracts_from_company_class(self, sample_entry):
        job = JobEntry(sample_entry)
        assert job.company == 'Acme Corp'

    def test_falls_back_to_result_link_source(self, sample_entry_no_salary):
        job = JobEntry(sample_entry_no_salary)
        assert job.company == 'Startup Inc'


class TestLocation:
    def test_extracts_city_state_zipcode_neighborhood(self, sample_entry):
        job = JobEntry(sample_entry)
        assert job.city == 'Boston'
        assert job.state.strip() == 'MA'
        assert job.zipcode == '02109'
        assert job.neighborhood == 'Downtown'

    def test_location_without_zipcode(self, sample_entry_no_salary):
        job = JobEntry(sample_entry_no_salary)
        assert job.city == 'Cambridge'
        assert job.state == 'MA'


class TestSalary:
    def test_extracts_from_nobr(self, sample_entry):
        job = JobEntry(sample_entry)
        assert job.salary == '$100,000 - $150,000 a year'

    def test_no_salary_returns_space(self, sample_entry_no_salary):
        job = JobEntry(sample_entry_no_salary)
        assert job.salary == ' '

    def test_extracts_from_salary_snippet(self, sample_entry_salary_snippet):
        job = JobEntry(sample_entry_salary_snippet)
        assert job.salary == '$120,000 - $180,000 a year'


class TestLink:
    def test_extracts_job_key(self, sample_entry):
        job = JobEntry(sample_entry)
        assert job.link == 'abc123def456'


class TestSummary:
    def test_extracts_summary(self, sample_entry):
        job = JobEntry(sample_entry)
        assert 'experienced data scientist' in job.summary


class TestToDict:
    def test_returns_all_fields(self, sample_entry):
        job = JobEntry(sample_entry)
        d = job.to_dict()
        assert d['job_title'] == 'Senior Data Scientist'
        assert d['company_name'] == 'Acme Corp'
        assert d['salary'] == '$100,000 - $150,000 a year'
        assert d['link'] == 'abc123def456'
        assert d['city'] == 'Boston'
