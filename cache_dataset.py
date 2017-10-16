"""
This module loads the entire dataset and saves it into a *.pickle file for later loading (with it being much faster)
"""

import os
from time import time

from linkedin.profile_manager import ProfileManager


# Inputs
html_dir = os.path.join(os.getcwd(), "Dataset", "HTML_Profiles")
json_dir = os.path.join(os.getcwd(), "Dataset", "JSON_Profiles")


print("Loading all profiles...")
start = time()
reader = ProfileManager(html_dir=html_dir, json_dir=json_dir, pre_cache_profiles=True)
print("Loaded", len(reader), "profiles in", time() - start, "seconds")

# Open all files in the ScrapedProfiles directory, parse, and print them

start = time()
print("Processing all profiles...")
for profile in reader:
    profile.name
    profile.name
    profile.username
    profile.skills
    profile.current_company
    profile.all_companies
    profile.location
    profile.connection_count
print("Processed all profiles in", time() - start, "seconds")

# Saving State
reader.save_state("./cached_dataset.pickle")