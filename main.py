from profile_parser import LipParser

"""
This module doesn't have anything important yet, it's just for testing existing stuff. 
Eventually it'll be where we run the main program.
"""

profiles = [LipParser("AG.html"),
            LipParser("AT.html"),
            LipParser("BA.html")]


for profile in profiles:
    print("Name: ", profile.get_name())
    print("Companies: ", profile.get_all_companies())
    print("Bio: ", profile.get_bio())
    print("Certifications: ", profile.get_certification())
    print("Current Company: ", profile.get_current_company())
    print("Languages: ", profile.get_languages())
    print("Location: ", profile.get_location())
    print("Skills: ", profile.get_skills())
    print("Projects: ", profile.get_projects())
    print("Connection #: ", profile.get_connection_number())
    print("Media #: ", profile.get_media_number())

    print("\n\n")