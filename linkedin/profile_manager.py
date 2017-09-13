import os
import ujson as json
from multiprocessing import Process, Pipe
import sys
import pickle

from linkedin.html_profile import HTMLProfile
from linkedin.json_profile import JSONProfile
from linkedin.profile_utils import cache

# def worker(html_list, output_pipe, pre_cache_profiles=False):
#     """ This class will get files from the work_queue, parse the HTML,
#     then add the Profile to self.profiles"""
#
#     sys.setrecursionlimit(15000)  # So that pickling BeautifulSoup objects will work
#     finished_profiles = []
#     for html in html_list:
#         profile = HTMLProfile(html)
#
#         if pre_cache_profiles:
#             profile.pre_cache_all()
#         finished_profiles.append(profile)
#     output_pipe.send(finished_profiles)



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

        # # My shitty multiprocessing code that sometimes works
        # def split(lst, n_parts):
        #     """ Split a list into even parts (for divvying work to workers"""
        #     k, m = divmod(len(lst), n_parts)
        #     return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n_parts))
        #
        # worker_cnt = 10
        #
        # html_list = []
        # parent_conn, child_con = Pipe()
        # for file in os.listdir(self.profiles_dir):
        #     profile_path = os.path.join(self.profiles_dir, file)
        #     with open(profile_path, encoding='utf8') as html_file:
        #         html_str = html_file.read()
        #     html_list.append(html_str)
        #
        # # Start the workers
        # worker_pool = []
        # for html_for_worker in split(html_list, worker_cnt):
        #     new_worker = Process(target=worker, args=(html_for_worker, child_con, pre_cache_profiles))
        #     new_worker.start()
        #     worker_pool.append(new_worker)
        #
        # # Wait for all work to be done, then rejoin all the threads
        # while len(self.profiles) != len(html_list):
        #     self.profiles += parent_conn.recv()
        #     print("ProfileManager Loaded", len(self.profiles), "profiles")
        #
        # [worker.join(1) for worker in worker_pool]

    def _load_state(self, load_from):
        """ Load a *.pickle of self.profiles """
        self.profiles = pickle.load(open(load_from, "rb"))


