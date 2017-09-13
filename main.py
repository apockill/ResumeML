import os
from time import time

from linkedin.profile_manager import ProfileManager


if __name__ == "__main__":
    # Inputs

    print("Loading all profiles...")
    start = time()
    reader = ProfileManager(load_pickle="./cached_dataset.pickle", pre_cache_profiles=False)
    print("Loaded", len(reader), "profiles in", time() - start, "seconds")

    # Open all files in the ScrapedProfiles directory, parse, and print them

    start = time()
    print("Processing all profiles...")
    for profile in reader:
        profile.name
        profile.username
        profile.skills
        profile.current_company
        profile.all_companies
        profile.location
        profile.connection_count

        # print("Name", profile.name)
        # print("Username", profile.username)
        # print("Skills", profile.skills)
        # print("Company", profile.current_company)
        # print("All Companies", profile.all_companies)
        # print("Location", profile.location)
        # print("Connections", profile.connection_count)
        # print("\n\n")
    print("Processed all profiles in", time() - start, "seconds")

    # print("All Users: ", reader.users)
    # print("All Skills: ", reader.skills)
    print("User Count: ", len(reader.users))
    # print("Skill Count: ", len(reader.skills))
