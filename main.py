import os
from linkedin.profile_manager import ProfileManager

"""
This module doesn't have anything important yet, it's just for testing existing stuff. 
Eventually it'll be where we run the main program.
"""


profiles_dir = os.path.join(os.getcwd(), "ScrapedProfiles")
reader = ProfileManager(profiles_dir)

# Open all files in the ScrapedProfiles directory, parse, and print them

for profile in reader:
    print(profile.name)
    print(profile.username)
    print(profile.skills)
    print(profile.current_company)
    print(profile.all_companies)
    print(profile.location)
    print(profile.connection_count)
    print("\n\n")

# print("All Users: ", reader.users)
print("All Skills: ", reader.skills)
