import os
from collections import Counter
from multiprocessing import Process, Pipe
import sys

from linkedin.profile_parser import Profile


sys.setrecursionlimit(10000)  # So that pickling BeautifulSoup objects will work -,-


def worker(html_list, output_pipe):
    """ This class will get files from the work_queue, parse the HTML,
    then add the Profile to self.profiles"""
    print("Starting worker")
    finished_profiles = []
    for html in html_list:
        finished_profiles.append(Profile(html))
    output_pipe.send(finished_profiles)


class ProfileManager:
    """
    This class handles loading many profiles into memory and searching through them.

    It has various helper functions for handling many profiles at once.

    It is also the safest way to write new profiles down. It automatically checks that a profile doesn't exist
    before creating a new one.
    """

    def __init__(self, profiles_dir):
        self.profiles_dir = profiles_dir

        self.profiles = []
        self._load_profiles()


    def __len__(self):
        return len(self.profiles)

    def __iter__(self):
        for profile in self.profiles:
            yield profile

    @property
    def users(self):
        return [p.username for p in self.profiles]

    @property
    def skills(self):
        """ Returns all skills from all users, with duplicates , in order of how common the skill was """
        skills = []
        for profile in self.profiles:
            skills += profile.skills

        ordered = sorted(skills, key=skills.count, reverse=True)
        print(Counter(ordered))
        no_duplicates = []
        [no_duplicates.append(skill) for skill in ordered if not no_duplicates.count(skill)]


        print("Total Skills", len(ordered), "nodupes", len(no_duplicates))
        return no_duplicates

    def write_new(self, html):
        """ This will check that there is no existing profile for this html and then write it if it is new """
        profile = Profile(html)

        if profile.username in self.users:
            print("ERROR: Tried to add", profile.username, "when it was already scraped!")
            return

        # Write to file
        write_to = os.path.join(self.profiles_dir, profile.username + ".html")
        if write_to in os.listdir(self.profiles_dir):
            print("ERROR: A filename of the same name already existed!", write_to)
            return

        with open(write_to, "wb") as new_file:
            new_file.write(str(html).encode("utf-8"))

        self.profiles.append(profile)


    def _load_profiles(self):
        """Load all profile in the profiles directory"""
        for file in os.listdir(self.profiles_dir):
            profile_path = os.path.join(self.profiles_dir, file)
            with open(profile_path, encoding='utf8') as html_file:
                html_str = html_file.read()
            self.profiles.append(Profile(html_str))


        return

        # My shitty multiprocessing code that sometimes works
        def split(lst, n_parts):
            """ Split a list into even parts (for divvying work to workers"""
            k, m = divmod(len(lst), n_parts)
            return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n_parts))

        worker_cnt = 12

        html_list = []
        parent_conn, child_con = Pipe()
        for file in os.listdir(self.profiles_dir):
            profile_path = os.path.join(self.profiles_dir, file)
            with open(profile_path, encoding='utf8') as html_file:
                html_str = html_file.read()
            html_list.append(html_str)

        # Start the workers, wait for all work to be done, then rejoin all threads
        worker_pool = []
        for html_for_worker in split(html_list, worker_cnt):
            print(len(html_for_worker))
            worker_pool.append(Process(target=worker, args=(html_for_worker, child_con)))

        [worker.start() for worker in worker_pool]

        while len(self.profiles) != len(html_list):
            self.profiles += parent_conn.recv()
            print("Received: ", len(self.profiles))

        [worker.join(1) for worker in worker_pool]


