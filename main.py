import os

from linkedin.profile_manager import ProfileManager

"""
This module doesn't have anything important yet, it's just for testing existing stuff. 
Eventually it'll be where we run the main program.
"""


profiles_dir = os.path.join(os.getcwd(), "ScrapedProfiles")

# Open all files in the ScrapedProfiles directory, parse, and print them
for profile in ProfileManager(profiles_dir):

    print("Name: ", profile.name)
    print("URL Name: ", profile.username)
    print("Skills: ", profile.skills)
    print("Current Company: ", profile.current_company)
    print("Companies: ", profile.all_companies)
    print("Location: ", profile.location)
    print("Connections : ", profile.connection_count)

    # print("Bio: ", profile.get_bio())
    # print("Certifications: ", profile.get_certification())
    # print("Languages: ", profile.get_languages())
    # print("Location: ", profile.get_location())
    # print("Projects: ", profile.get_projects())
    # print("Media #: ", profile.get_media_number())

    print("\n\n")

