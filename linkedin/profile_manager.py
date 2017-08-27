import os
from linkedin.profile_parser import Profile


class ProfileManager:
    """
    This class handles loading many profiles into memory and searching through them.

    It has various helper functions for handling many profiles at once.

    """

    def __init__(self, profiles_dir):
        self.directory = profiles_dir

        self.profiles = []

        # Load all profile in the profiles_dir
        for file in os.listdir(profiles_dir):
            profile_path = os.path.join(profiles_dir, file)

            with open(profile_path, encoding='utf8') as html_file:
                html_str = html_file.read()

            self.profiles.append(Profile(html_str))


    def __iter__(self):
        for profile in self.profiles:
            yield profile