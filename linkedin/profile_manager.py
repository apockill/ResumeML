import os
import ujson as json
import sys
import pickle

from linkedin.html_profile import HTMLProfile
from linkedin.json_profile import JSONProfile





class ProfileManager:
    """
    This class handles loading many profiles into memory and searching through them.

    It has various helper functions for handling many profiles at once.

    It is also the safest way to write new profiles down. It automatically checks that a profile doesn't exist
    before creating a new one.
    """

    def __init__(self, load_pickle=None, html_dir=None, json_dir=None, pre_cache_profiles=False):
        """
        :param load_pickle: A path to a *.pickle file of a previously saved state
        :param profiles_dir: The location where profiles are stored
        :param pre_cache_profiles: Whether or not to preprocess profiles during
        the loading process which is multithreaded, thus potentially saving time later
        """

        self._html_profiles_dir = html_dir
        self._json_profiles_dir = json_dir

        self.profiles = []
        if load_pickle is not None:
            self._load_state(load_pickle)

        self._load_profiles(pre_cache_profiles)

    def __len__(self):
        return len(self.profiles)

    def __iter__(self):
        for profile in self.profiles:
            yield profile


    @property
    def users(self):
        """ Returns a list of strings of users stored in the ProfileManager"""
        return [p.username for p in self.profiles]

    @property
    def skills(self):
        """ Returns all skills from all users, with duplicates , in order of how common the skill was """
        skills = []
        for profile in self.profiles:
            skills += profile.skills

        ordered = sorted(skills, key=skills.count, reverse=True)
        no_duplicates = []
        [no_duplicates.append(skill) for skill in ordered if not no_duplicates.count(skill)]


        print("Total Skills", len(ordered), "nodupes", len(no_duplicates))
        return no_duplicates

    def save_state(self, save_to):
        """
        Save a pickle of the internal self.profiles variable
        :param save_to: the path to where to save it
        """
        sys.setrecursionlimit(15000)  # Pickling BeautifulSoup objects is very recursion heavy
        pickle.dump(self.profiles, open(save_to, "wb"))

    def write_new_html_profile(self, html):
        """ This will check that there is no existing profile for this html and then write it if it is new """
        profile = HTMLProfile(html)

        if profile.username in self.users:
            print("ERROR: Tried to add", profile.username, "when it was already scraped!")
            return

        # Write to file
        write_to = os.path.join(self._html_profiles_dir, profile.username + ".html")
        if write_to in os.listdir(self._html_profiles_dir):
            print("ERROR: A filename of the same name already existed!", write_to)
            return

        with open(write_to, "wb") as new_file:
            new_file.write(str(html).encode("utf-8"))

        self.profiles.append(profile)

    def _load_profiles(self, pre_cache_profiles):
        """Load all profile in the profiles directory"""

        # Load all html profiles
        if self._html_profiles_dir is not None:
            for file in os.listdir(self._html_profiles_dir):
                profile_path = os.path.join(self._html_profiles_dir, file)
                with open(profile_path, encoding='utf8') as html_file:
                    html_str = html_file.read()
                self.profiles.append(HTMLProfile(html_str))

        # Load all the JSON profiles
        if self._json_profiles_dir is not None:
            for file in os.listdir(self._json_profiles_dir):
                json_path = os.path.join(self._json_profiles_dir, file)

                with open(json_path, encoding="utf-8") as file:
                    try:
                        file_str = file.read()
                        profile_jsons = json.loads(file_str)

                    except ValueError as e:
                        print("Failed to load: ", json_path)
                parsed_profiles = [JSONProfile(parsed) for parsed in profile_jsons]
                self.profiles += parsed_profiles

        print("Pre-caching Profiles")
        if pre_cache_profiles:
            for profile in self.profiles:
                profile.pre_cache_all()
        return


    def _load_state(self, load_from):
        """ Load a *.pickle of self.profiles """
        self.profiles = pickle.load(open(load_from, "rb"))


