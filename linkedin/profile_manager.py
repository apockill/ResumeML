import os
from linkedin.profile_parser import Profile



class ProfileManager:
    """
    This class handles loading many profiles into memory and searching through them.

    It has various helper functions for handling many profiles at once.

    It is also the safest way to write new profiles down. It automatically checks that a profile doesn't exist
    before creating a new one.
    """

    def __init__(self, profiles_dir):
        self.profile_dir = profiles_dir

        self.profiles = []
        self.x = 3
        # Load all profile in the profiles_dir
        print("Loading", len(os.listdir(profiles_dir)), "profiles into memory...")
        for file in os.listdir(profiles_dir):
            profile_path = os.path.join(profiles_dir, file)

            with open(profile_path, encoding='utf8') as html_file:
                html_str = html_file.read()

            self.profiles.append(Profile(html_str))
        print("Done Loading")

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
        no_duplicates = []
        [no_duplicates.append(skill) for skill in ordered if not no_duplicates.count(skill)]

        # print("Total Skills", len(ordered), "nodupes", len(no_duplicates))
        return no_duplicates

    def write_new(self, html):
        """ This will check that there is no existing profile for this html and then write it if it is new """
        profile = Profile(html)
        if profile.username in self.users:
            print("Tried to add", profile.username, "when it was already scraped!")
            return

        # Write to file
        write_to = os.path.join(self.profile_dir, profile.username + ".html")
        if write_to in os.listdir(self.profile_dir):
            print("ERROR: A filename of the same name already existed!", write_to)
            return

        with open(write_to, "wb") as new_file:
            new_file.write(str(html).encode("utf-8"))
            # print(str(html), file=new_file)




