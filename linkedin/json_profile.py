from bs4 import BeautifulSoup

from linkedin.profile_utils import cache


class JSONProfile:
    """
        This class receives HTML from a linkedin profile webpage, and offers many functions for
        scraping information from that webpage.
    """

    def __init__(self, profile_dict):
        """
        :param profile_dict: An already parsed JSON profile, in the form of a python dictionary
        """
        self.profile = profile_dict

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


    # Parsing Functions (Tested)
    @property
    @cache("__name")
    def name(self):
        """
        Default: ""
        :return: string name
        """

        name = ""
        if "first-name" in self.profile and "last-name" in self.profile:
            name = self.profile["first-name"] + " " + self.profile["last-name"]
        return name

    @property
    @cache("__skills")
    def skills(self):
        """
        :return: ['skill', 'skill', ...]
        """
        skills = []
        if "skills" in self.profile:
            skills = self.profile["skills"]

        return skills

    @property
    @cache("__username")
    def username(self):
        """
         :return: String, unique name
        """
        profile_url = self.profile["public-profile-url"]
        if "/pub/" in profile_url:
            username = profile_url.split(sep="/pub/", maxsplit=1)[1]
            username = username.split(sep="/")[0]

        if "/in/" in profile_url:
            username = profile_url.split("/in/", 1)[1]


        return username

    @property
    @cache("__location")
    def location(self):
        """
        Default: None
        :return: A string of where the person lives "San Fransisco Bay Area"
        """

        if "location" in self.profile and self.profile["location"] is not None:
            return self.profile["location"]

        return None

    @property
    @cache("__current_company")
    def current_company(self):
        """
        Gets this persons current company with a ton of spaces at the front and newlines??? Condition later
        Default: None

        Corner Cases:
            - It will attempt to return the explicit current company
            - If no company is EXPLICITLY stated, look for the latest held position
        :return: "current company"
        """

        if "company-name" in self.profile and self.profile["company-name"] is not None:
            company = self.profile["company-name"]
            return company

        if "positions" in self.profile:
            positions = self.profile["positions"]
            if "company-name" in positions[0] and positions[0]["company-name"] is not None:
                company = positions[0]["company-name"]
                return company

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
        companies = []

        if "positions" in self.profile:
            companies = [pos["company-name"] for pos in self.profile["positions"] if "company-name" in pos]

        return companies

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

        connections = 0
        if "num-connections" in self.profile:
            connections = self.profile["num-connections"]

        return connections
