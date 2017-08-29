import os
from time import time

from linkedin.profile_manager import ProfileManager


if __name__ == "__main__":
    print("Loading all profiles...")
    start = time()
    profiles_dir = os.path.join(os.getcwd(), "ScrapedProfiles")
    reader = ProfileManager(profiles_dir)
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
    print("Processed all profiles in", time() - start, "seconds")

    # print("All Users: ", reader.users)
    print("All Skills: ", reader.skills)
