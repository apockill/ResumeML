import os

from profile_parser import LipParser

"""
This module doesn't have anything important yet, it's just for testing existing stuff. 
Eventually it'll be where we run the main program.
"""




# Open all files in the Profiles directory, parse, and print them
for file in os.listdir("Profiles"):
    profile = LipParser(os.path.join("Profiles", file))

    print("Name: ", profile.get_name())
    print("URL Name: ", profile.get_profile_url())
    print("Skills: ", profile.get_skills(), len(profile.get_skills()))

    print("Companies: ", profile.get_all_companies())
<<<<<<< HEAD
    # print("Bio: ", profile.get_bio())
    # print("Certifications: ", profile.get_certification())
    # print("Current Company: ", profile.get_current_company())
    # print("Languages: ", profile.get_languages())
    # print("Location: ", profile.get_location())
    # print("Skills: ", profile.get_skills())
    # print("Projects: ", profile.get_projects())
    # print("Connection #: ", profile.get_connection_number())
    # print("Media #: ", profile.get_media_number())
=======
    print("Bio: ", profile.get_bio())
    print("Certifications: ", profile.get_certification())
    print("Current Company: ", profile.get_current_company())
    print("Languages: ", profile.get_languages())
    print("Location: ", profile.get_location())
    print("Skills: ", profile.get_skills())
    print("Projects: ", profile.get_projects())
    print("Honors & Awards: ", profile.get_awards())
    print("Organizations: ", profile.get_organizations())
    print("Courses: ", profile.get_courses())
    print("Connection #: ", profile.get_connection_number())
    print("Media #: ", profile.get_media_number())
>>>>>>> a80f7424e0eb53c64af2d3cb3123278fcc49e39d

    print("\n\n")