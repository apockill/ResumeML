from threading import RLock
import json



class CrawlerConfig:
    """
    A threading-proof class for accessing config files and settings
    """

    WEBSITES_FILE = "Websites.txt"
    SETTINGS_FILE = "Settings.json"

    DEFAULT_SETTINGS = {"sleep_google_search": (1, 3),
                        "sleep_linkedin":      (5, 20),
                        "sleep_random_break":  (30, 90),
                        "sleep_rate_limiting": (60, 120),
                        "sleep_timeout":       (150, 200),

                        "urls_between_break":  (10, 20),

                        "browser_timeout":     30}

    def __init__(self):
        self.lock = RLock()



    @property
    def sleep_google_search(self):
        return self.__load_from_settings("sleep_google_search")

    @property
    def sleep_linkedin(self):
        return self.__load_from_settings("sleep_linkedin")

    @property
    def sleep_random_break(self):
        return self.__load_from_settings("sleep_random_break")

    @property
    def sleep_rate_limiting(self):
        return self.__load_from_settings("sleep_rate_limiting")

    @property
    def sleep_timeout(self):
        return self.__load_from_settings("sleep_timeout")

    @property
    def urls_between_break(self):
        return self.__load_from_settings("urls_between_break")

    @property
    def browser_timeout(self):
        return self.__load_from_settings("browser_timeout")

    @browser_timeout.setter
    def browser_timeout(self, value):
        self.__save_to_settings("browser_timeout", value)

    @property
    def websites(self):
        """
        Tries to load a file with website list in the current directory.
        :return:
        """
        web_list = []
        with self.lock:
            try:
                with open(self.WEBSITES_FILE, "r") as file:
                    for line in file:
                        line = line.replace('\n', '')
                        web_list.append(line)
            except FileNotFoundError:
                # Return default empty value if the file does not exist
                return web_list

        return web_list

    # Helper Functions
    def __save_to_settings(self, key, val):
        """ Saves a settings to the settings file"""

        with self.lock:
            # Try to pull the current settings from the settings file. If that file doesn't exist, use the default
            try:
                with open(self.SETTINGS_FILE, 'r') as file:
                    data = json.load(file)

            except FileNotFoundError:
                data = self.DEFAULT_SETTINGS

            # Change the setting
            data[key] = val

            # Write the setting to file
            with open(self.SETTINGS_FILE, 'w') as file:
                json.dump(data, file)

    def __load_from_settings(self, key):
        """ Tries to load from settings.json, returns default value otherwise """

        with self.lock:
            try:
                with open(self.SETTINGS_FILE, 'r') as file:
                    data = json.load(file)

            except FileNotFoundError:
                # If the Settings.json file has not yet been created, generate it
                with open(self.SETTINGS_FILE, 'w') as file:
                    json.dump(self.DEFAULT_SETTINGS, file)

                return self.DEFAULT_SETTINGS[key]

        return data[key]