"""Tests for JobEntry.py parsing functions."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from JobEntry import (
    get_job_title,
    get_company,
    get_location_info,
    get_salary,
    get_link,
    get_job_summary,
    get_zipcode,
    get_city_and_state,
    get_neighborhood,
)


class TestGetJobTitle:
    def test_extracts_title(self, sample_entry):
        assert get_job_title(sample_entry) == 'Senior Data Scientist'

    def test_strips_whitespace(self, sample_entry):
        title = get_job_title(sample_entry)
        assert title == title.strip()


class TestGetCompany:
    def test_extracts_from_company_class(self, sample_entry):
        assert get_company(sample_entry) == 'Acme Corp'

    def test_falls_back_to_result_link_source(self, sample_entry_no_salary):
        assert get_company(sample_entry_no_salary) == 'Startup Inc'


class TestGetLocationInfo:
    def test_extracts_city_state_zipcode_neighborhood(self, sample_entry):
        city, state, zipcode, neighborhood = get_location_info(sample_entry)
        assert city == 'Boston'
        assert state.strip() == 'MA'
        assert zipcode == '02109'
        assert neighborhood == 'Downtown'

    def test_location_without_zipcode(self, sample_entry_no_salary):
        city, state, zipcode, neighborhood = get_location_info(sample_entry_no_salary)
        assert city == 'Cambridge'
        assert state == 'MA'


class TestGetZipcode:
    def test_extracts_zipcode(self):
        assert get_zipcode('Boston, MA 02109') == '02109'

    def test_no_zipcode_returns_space(self):
        assert get_zipcode('Cambridge, MA') == ' '


class TestGetCityAndState:
    def test_splits_city_and_state(self):
        city, state = get_city_and_state('Boston, MA')
        assert city == 'Boston'
        assert state == 'MA'


class TestGetNeighborhood:
    def test_extracts_neighborhood(self, sample_entry):
        location_info = sample_entry.find(class_='sjcl').find(class_='location')
        neighborhood = get_neighborhood(location_info)
        assert 'Downtown' in neighborhood

    def test_no_neighborhood(self, sample_entry_no_salary):
        location_info = sample_entry_no_salary.find(class_='sjcl').find(class_='location')
        neighborhood = get_neighborhood(location_info)
        assert neighborhood.strip() == ''  # no span child


class TestGetSalary:
    def test_extracts_from_nobr(self, sample_entry):
        salary = get_salary(sample_entry)
        assert '$100,000 - $150,000 a year' == salary

    def test_no_salary_returns_space(self, sample_entry_no_salary):
        salary = get_salary(sample_entry_no_salary)
        assert salary == ' '

    def test_extracts_from_salary_snippet(self, sample_entry_salary_snippet):
        salary = get_salary(sample_entry_salary_snippet)
        assert '$120,000 - $180,000 a year' == salary


class TestGetLink:
    def test_extracts_job_key(self, sample_entry):
        assert get_link(sample_entry) == 'abc123def456'


class TestGetJobSummary:
    def test_extracts_summary(self, sample_entry):
        summary = get_job_summary(sample_entry)
        assert 'experienced data scientist' in summary
