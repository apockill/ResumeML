#  REALLY NEED TO MAKE SURE ALL SECTIONS OF LIP ARE EXPANDED BEFORE ACQUISITION
#  ============================================================================

from bs4 import BeautifulSoup
import os.path


class LipParser:  # No, we're not reading Lips, we're parsing Linked In Profiles

    def __init__(self, file_name):  # Assumes that file is in same location as path
        scriptpath = os.path.dirname(__file__)
        filepath = os.path.join(scriptpath, file_name)
        with open(filepath, encoding='utf8') as fp:
            self.soup = BeautifulSoup(fp, "html.parser")

    def get_name(self):  # Finds the name of the Lip holder
        name = self.soup.find(class_="pv-top-card-section__name Sans-26px-black-85%").string
        return name

    def get_bio(self):  # Returns the bio without new-lines
        bio_tag = self.soup.find(class_="pv-top-card-section__summary Sans-15px-black-70% mt5 pt5 ember-view")
        bio = ""
        for string in bio_tag.strings:  # P seems to be content in paragraphs
            if string != "See more":
                bio = bio + string

            else:
                break

        return bio.replace("\n", "")

    def get_location(self):
        return self.soup.find(class_="pv-top-card-section__location Sans-17px-black-70% mb1 inline-block").string

    def get_current_company(self):  # Returns company with a ton of spaces at the front? Condition later
        company = self.soup.find(class_="pv-top-card-section__company Sans-17px-black-70% mb1 inline-block").string
        return company

    def get_all_companies(self):  # Returns all companies in experience section
        experience_tag = self.soup.find(class_="pv-profile-section experience-section ember-view")
        companies_array = []
        for company in experience_tag.find_all(class_="pv-entity__secondary-title"):
            companies_array.append(company.string)
        return companies_array

    def get_skills(self):  # Get skills from skills section (skills section has to be expanded before acquiring html)
        skills_array = []
        for skill in self.soup.find_all(class_="pv-skill-entity__skill-name"):
            skills_array.append(skill.string)
        return skills_array  # Could also return the number of skills. Also endorsements?

    def get_media_number(self):  # Probably considered an ugly way to do this but it works
        media_title = self.soup.find(class_="pv-treasury-carousel__subheadline").string
        media_num = 0
        for character in media_title:
            print(character)
            if character.isdigit():
                media_num = media_num * 10 + int(character)
        return media_num

    def get_languages(self):  # The following two methods could be condensed into one method (including this one) with another param if desired.
        accomp_tag = self.soup.find(class_="pv-profile-section artdeco-container-card pv-accomplishments-section ember-view")
        languages_array = []
        for section in accomp_tag.find_all(class_="pv-accomplishments-block__title"):
            if section.string == "Languages":
                for language in section.parent.find_all(class_="pv-accomplishments-block__summary-list-item"):
                    languages_array.append(language.string)
                break
        return languages_array

    def get_certification(self):
        accomp_tag = self.soup.find(class_="pv-profile-section artdeco-container-card pv-accomplishments-section ember-view")
        cert_array = []
        for section in accomp_tag.find_all(class_="pv-accomplishments-block__title"):
            if section.string == "Certification":
                for certification in section.parent.find_all(class_="pv-accomplishments-block__summary-list-item"):
                    cert_array.append(certification.string)
                break
        return cert_array

    def get_projects(self):
        accomp_tag = self.soup.find(class_="pv-profile-section artdeco-container-card pv-accomplishments-section ember-view")
        proj_array = []
        for section in accomp_tag.find_all(class_="pv-accomplishments-block__title"):
            if section.string == "Projects":
                for project in section.parent.find_all(class_="pv-accomplishments-block__summary-list-item"):
                    proj_array.append(project.string)
                break
        return proj_array

    def get_connection_number(self):
        conn_tag = self.soup.find(class_="pv-top-card-section__connections pv-top-card-section__connections--with-separator Sans-17px-black-70% mb1 inline-block")
        cons = 0
        for string in conn_tag.strings:
            if string.isdigit():
                cons = int(string)
        return cons


AG = LipParser("AG.html")
AT = LipParser("AT.html")
BA = LipParser("BA.html")
print(AT.get_bio())


# =================================
# Some useful commands here as reference


#  print(AT.soup.contents)

# for child in AT.soup.find(class_="pv-profile-section experience-section ember-view").children:
#     print(child.find_all("h3"))


# print(soup.prettify())  # Print out slightly prettier version of html hell

# text = soup.get_text() # Get text from html
# text = text.replace(' ', '')

# for link in soup.find_all('a'): # Print out found links
#     print(link.get('href'))
