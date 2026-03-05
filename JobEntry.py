"""Parsed representation of an Indeed job posting entry."""

import time
from functools import cached_property

import requests
from bs4 import BeautifulSoup


class JobEntry:
    """Wraps a BeautifulSoup element for a single Indeed search result row."""

    def __init__(self, entry):
        self._entry = entry

    @cached_property
    def job_title(self):
        container = self._entry.find(name='a', attrs={'data-tn-element': 'jobTitle'})
        return container.text.strip()

    @cached_property
    def company(self):
        try:
            return self._entry.find(class_='company').text.strip()
        except AttributeError:
            try:
                return self._entry.find(class_='result-link-source').text.strip()
            except AttributeError:
                return ' '

    @cached_property
    def _location(self):
        company_info = self._entry.find(class_='sjcl')
        location_info = company_info.find(class_='location')
        location = location_info.text.strip()

        # extract neighborhood
        neighborhood_info = location_info.find(name='span')
        neighborhood = ' '
        if neighborhood_info:
            neighborhood = neighborhood_info.text
        location = location.rstrip(neighborhood)
        neighborhood = neighborhood.strip('()')

        # extract zipcode
        zipcode = ' '
        temp = [s for s in location.split() if s.isdigit()]
        if temp:
            zipcode = temp.pop()
        location = location.strip(zipcode)

        # split city and state
        city_state = location.split(', ')
        state = city_state.pop()
        city = city_state.pop()

        return city, state, zipcode, neighborhood

    @property
    def city(self):
        return self._location[0]

    @property
    def state(self):
        return self._location[1]

    @property
    def zipcode(self):
        return self._location[2]

    @property
    def neighborhood(self):
        return self._location[3]

    @cached_property
    def salary(self):
        try:
            return self._entry.find('nobr').text.strip()
        except AttributeError:
            try:
                container = self._entry.find(name='div', class_='salarySnippet')
                return container.find(name='span', class_='salary').text.strip()
            except AttributeError:
                return ' '

    @cached_property
    def link(self):
        return self._entry['data-jk']

    @cached_property
    def summary(self):
        return self._entry.find(class_='summary').text.strip()

    def to_dict(self):
        return {
            'job_title': self.job_title,
            'company_name': self.company,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zipcode,
            'neighborhood': self.neighborhood,
            'salary': self.salary,
            'link': self.link,
        }

    @staticmethod
    def fetch_description(job_url):
        page = requests.get(job_url)
        time.sleep(1)  # ensuring at least 1 second between page grabs
        soup = BeautifulSoup(page.text, 'lxml')
        description = soup.find(name='div', id='jobDescriptionText')
        text = description.text.strip()
        return text.replace('\n', ' ').replace('\t', ' ')
