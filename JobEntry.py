class JobEntry:
    from bs4 import BeautifulSoup
    from requests

    def __init__(self, entry):
        self.entry = entry


    def get_job_title(entry):
        job_title_container = entry.find(name='a', attrs={'data-tn-element':'jobTitle'})
        job_title = job_title_container.text
        return job_title.strip()

    def get_company(entry):
        company_list = []
        try:
            test_entry = entry.find(class_='company')
            company_list.append(test_entry.text.strip())
            company = company_list.pop()
        except:
            try:
                test_entry = entry.find(class_='result-link-source')
                company_list.append(test_entry.text.strip())
                company = company_list.pop()
            except:
                company = ' '
        return company

    def get_location_info(entry):
        company_info = entry.find(class_='sjcl')
        location_info = company_info.find(class_='location')

        location = location_info.text.strip()

        # extract neightborhood info if it's there
        neighborhood = get_neighborhood(location_info)
        location = location.rstrip(neighborhood)
        neighborhood = neighborhood.strip('()')

        # extract the zipcode from location if it's there
        zipcode = get_zipcode(location)
        location = location.strip(zipcode)

        city, state = get_city_and_state(location)

        return city, state, zipcode, neighborhood

    def get_city_and_state(location):
        city_state = location.split(', ')
        state = city_state.pop()
        city = city_state.pop()
        return city, state

    def get_neighborhood(location_info):
        neighborhood_info = location_info.find(name='span')
        neighborhood = ' '
        if neighborhood_info:
            neighborhood = neighborhood_info.text
        return neighborhood

    def get_zipcode(location):
        zipcode = ' '
        temp = [ s for s in location.split() if s.isdigit() ]
        if temp:
            zipcode = temp.pop()
        return zipcode

    def get_salary(entry):
        salary_list = []
        salary = ''
        try:
            salary_list.append(entry.find('nobr').text.strip())
            salary = salary_list.pop()
        except:
            try:
                salary_container = entry.find(name='div', class_='salarySnippet')
                salary_temp = salary_container.find(name='span', class_='salary')
                salary_list.append(salary_temp.text.strip())
                salary = salary_list.pop()
            except:
                salary = ' '
        return salary

    def get_link(entry):
        link = entry['data-jk']
        return link

    def get_job_description(job_page):
        page = requests.get(job_page)
        time.sleep(1)  #ensuring at least 1 second between page grabs
        soup = BeautifulSoup(page.text, 'lxml')

        # Loop over posts/entries
        description = soup.find(name='div', id='jobDescriptionText')

        description = description.text.strip()
        description = description.replace('\n',' ')
        description = description.replace('\t',' ')
        return description
    
    def get_job_summary(entry):
        return entry.find(class_='summary').text.strip()

