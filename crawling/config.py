from threading import RLock
import json



class Config:
    """
    A threading-proof class for accessing config files and settings
    """


    DEFAULT_SETTINGS = {"driver_path": "Resources/phantomjs.exe",
                        "browser_timeout": 30,
                        "max_browser_instances": 1}

    def __init__(self, websites_file, settings_file):
        """
        :param websites_file:
        The websites file is a text file where every line is a URL for a "seed" website that supposedly has links to
        other linkedin profiles in it. Ideally, it would be a search page on linkedin.

        :param settings_file:
        The settings file is a JSON formatted file with the parameters shown below. It decides how the crawler script
        will act.
        """
        self.WEBSITES_FILE = websites_file
        self.SETTINGS_FILE = settings_file
        self.lock = RLock()


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

    # @websites.setter
    # def websites(self, website_list):
    #     """
    #     Saves the website list to a file. If the file doesn't exist, it will create it.
    #     :param website_list: ['website', 'website']
    #     :return: Nothing
    #     """
    #     file_str = ""
    #     for line in website_list:
    #         file_str += line + "\n"
    #
    #     with self.lock:
    #         with open(self.WEBSITES_FILE, 'w') as file:
    #             file.write(file_str)

    @property
    def max_depth(self):
        return self.__load_from_settings("max_depth")

    @property
    def max_browser_instances(self):
        return self.__load_from_settings("max_browser_instances")

    # @max_browser_instances.setter
    # def max_browser_instances(self, value):
    #     self.__save_to_settings("max_browser_instances", value)


    @property
    def browser_timeout(self):
        return self.__load_from_settings("browser_timeout")

    # @browser_timeout.setter
    # def browser_timeout(self, value):
    #     self.__save_to_settings("browser_timeout", value)


    # # Helper Functions
    # def __save_to_settings(self, key, val):
    #     """ Saves a settings to the settings file"""
    #
    #
    #     with self.lock:
    #         # Try to pull the current settings from the settings file. If that file doesn't exist, use the default
    #         try:
    #             with open(self.SETTINGS_FILE, 'r') as file:
    #                 data = json.load(file)
    #
    #         except FileNotFoundError:
    #             data = self.DEFAULT_SETTINGS
    #
    #         # Change the setting
    #         data[key] = val
    #
    #         # Write the setting to file
    #         with open(self.SETTINGS_FILE, 'w') as file:
    #             json.dump(data, file)

    def __load_from_settings(self, key):
        """ Tries to load from settings.json, returns default value otherwise """

        with self.lock:
            try:
                with open(self.SETTINGS_FILE, 'r') as file:
                    data = json.load(file)

            except FileNotFoundError:
                return self.DEFAULT_SETTINGS[key]

        return data[key]