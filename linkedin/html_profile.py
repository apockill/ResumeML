from bs4 import BeautifulSoup

from linkedin.profile_utils import cache


class HTMLProfile:
    """
        This class receives HTML from a linkedin profile webpage, and offers many functions for
        scraping information from that webpage.
    """

    def __init__(self, html_str):
        """
        :param html_str: The string of the html file of the persons profile
        """

        self.soup = BeautifulSoup(html_str, "lxml")

    def pre_cache_all(self):
        """
        This will run all functions that can be cached, all at once. This is useful when multithreading the
        loading of many profiles, which saves CPU time down the line
        """
        self.name
        self.username
        self.skills
        self.current_company
        self.all_companies
        self.location
        self.connection_count
        self.industry

    # Parsing Functions (Tested)
    @property
    @cache("__name")
    def name(self):
        """
        Finds the name of the Lip holder
        Default: ""
        :return: string name
        """

        name = self.soup.find(class_="pv-top-card-section__name Sans-26px-black-85%")
        if name is not None:
            return name.string

        name = self.soup.find(id="name")
        if name is not None:
            return name.string

        if name is None:
            return ""
        return name

    @property
    @cache("__skills")
    def skills(self):
        """
        Default: []

        Get skills from skills section (skills section has to be expanded before acquiring html)

        Future: Could also return the number of skills. Also endorsements?
        :return: ['skill', 'skill', ...]
        """

        skills_html = self.soup.find_all(class_="pv-skill-entity__skill-name")
        if len(skills_html) == 0:
            skills_html = self.soup.find_all(class_="skill")

        skills_array = []

        for skill in skills_html:
            # Get rid of the "See X+" and "See less" buttons that pop up under skills
            if "see-more" in skill.get_attribute_list('class'): continue
            if "see-less" in skill.get_attribute_list('class'): continue

            if skill.find_all(class_="skill see-more"): continue

            sanitized_skill = skill.string.lower()
            sanitized_skill = sanitized_skill.strip()
            skills_array.append(sanitized_skill)

        return skills_array

    @property
    @cache("__username")
    def username(self):
        """ Gets the name of the person from the URL of the page. This is useful for when you need a unique name
         of a person.
         :return: String, unique name"""

        url_links = self.soup.find_all('link', rel="canonical", href=True)
        if len(url_links) == 0:
            print("Error loading username: ", self.name)
            return None
        profile_url = url_links[0]['href']
        username = profile_url.split("/in/", 1)[1]
        return username

    @property
    @cache("__location")
    def location(self):
        """
        Where the user lives
        Default: None
        :return: "San Fransisco Bay Area"
        """
        location_tag = self.soup.find(class_="locality")
        if location_tag is not None and location_tag.string is not None:
            return location_tag.string

        return None

    @property
    @cache("__current_company")
    def current_company(self):
        """
        Gets this persons current company with a ton of spaces at the front and newlines??? Condition later
        Default: None
        Corner Cases:
            - It will attempt to return the explicit current company
            - If no company is EXPLICITLY stated, look for current position
            - If no current position is EXPLICITLY stated, look for latest company under Experience
            - If no Experience, return None
        :return: "current company"
        """

        company_tag = self.soup.find(attrs={"data-section": "currentPositionsDetails"})
        if company_tag is not None:
            current_company = company_tag.find(class_="org").string
            if current_company is not None:
                return current_company

        companies = self.all_companies
        if len(companies) != 0 and companies[0] is not None:
            return companies[0]

        companies = self.soup.find(class_="headline title")
        if companies is not None and companies.string is not None:
            return companies.string

        return None

    @property
    @cache("__all_companies")
    def all_companies(self):
        """
        Returns all companies in experience section
        Default: []
        :return: ["company", "company"]
        if no companies found return empty array
        """

        experience_tag = self.soup.find(class_="positions")
        if experience_tag is None:
            return []
        companies_array = []

        for company in experience_tag.find_all(class_="item-subtitle"):
            companies_array.append(company.string)

        return companies_array

    @property
    @cache("__connection_count")
    def connection_count(self):
        """
        Get this persons number of LinkedIn Connections
        Default: 0
        Corner Cases:
            Some profiles have "Influencer" instead of a connection number. These default to None (Currently)
        :return: number
        """
        conn_tag = self.soup.find(class_="member-connections")

        if conn_tag is None:
            return 0

        cons = 0
        for string in conn_tag.strings:
            if string.isdigit():
                cons = int(string)

            elif string == "500+":
                cons = 500

        return cons


    @property
    @cache("__industry")
    def industry(self):
        """
        Default: None
        :return: The industry that the person works in
        """
        industry_tag = self.soup.find_all("dd", class_="descriptor")

        if len(industry_tag) == 2 and industry_tag[1].string is not None:
            return industry_tag[1].string

        return None