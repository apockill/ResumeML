from time import sleep
from urllib.parse import urljoin
from random import uniform, randint, shuffle, choice
import os

from selenium.webdriver import Chrome as Driver
from selenium.webdriver import ChromeOptions as Options
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class Crawler:
    def __init__(self, profile_manager, driver_path, config):
        """
        :param profile_manager: A ProfileManager object with all profiles loaded already
        :param driver_path: The path to the browser driver that is being used for scraping
        :param config: A CrawlerConfig object
        """

        # Parameters
        self.cfg = config
        self.driver_path = driver_path

        # Controls
        self.profile_manager = profile_manager
        self.crawled_urls = []
        self.profiles_since_break = 0
        self.browser = None
        self.current_agent = None

    def run(self):
        """ This runs in a new thread when crawler.run() is called """

        self._start_browser()

        # Start crawling each URL
        for url in self.cfg.websites:
            print("Starting Crawling on Seed: ", url)
            self._crawl_page(url)

        self._close_browser()

    def _crawl_page(self, url):
        """
        If the url is a linkedin url, it will check if it is a profile, save it, and add it to crawled URL's.

        If the url is NOT a linkedin url (thus a google search page), it will find linkedin URL's and crawl them.
        It will also find "next search page" arrows on google, and crawl those as well.

        :param url: The link to crawl
        :return:
        """

        if url in self.crawled_urls:
            print("Tried to crawl the same URL twice in one session", url)
            return

        self.crawled_urls.append(url)

        if self.profiles_since_break > randint(*self.cfg.urls_between_break):
            self._take_break(self.cfg.sleep_random_break,
                             "Taking break after " + str(self.profiles_since_break) + " profiles !")



        # If it is a linkedin profile currently being crawled, save the HTML
        if "linkedin" in url and "/in/" in url and url.count("/") == 4:

            # Check that this profile has not been parsed before
            username = url.split("/in/", 1)[1]
            if username in self.profile_manager.users:
                print("Already crawled: ", username)
                return

            print("Analyzing Profile #", len(self.profile_manager), url, username)

            # Load the page
            html = self._load_page(url)
            self.profiles_since_break += 1

            # If linkedin rate-limited us, continue to the next profile
            if html is None: return

            # Save HTML to a file
            # TODO: Fix this
            try:
                self.profile_manager.write_new_html_profile(html)
            except Exception as e:
                print("ERROR: While saving HTML: ", e, " in url: ", url)

        elif "www.google.com" in url:
            # Load the page
            html = self._load_page(url)

            # If it is a google search page currently being crawled to find more linkedin profiles
            linkedin_urls = self._get_results_urls(html)
            shuffle(linkedin_urls)
            for url in linkedin_urls:
                self._crawl_page(url)

            # Get the "Next" link to go to the next page of results
            soup = BeautifulSoup(html, "lxml")
            next_link = soup.find("a", {"id": "pnnext"})
            if next_link is not None:
                next_link = urljoin("http://www.google.com", next_link["href"])
                self._crawl_page(next_link)
        else:
            print("ERROR: Tried to crawl bad url: ", url)

    def _get_results_urls(self, html):
        # Get links to results from a google search
        links = []
        soup = BeautifulSoup(html, "lxml")

        for link in soup.find_all('cite', class_="_Rm"):
            links.append(link.text)

        return links

    def _load_page(self, url):
        # Load the page
        try:
            self.browser.get(url)
            html = self.browser.page_source
        except TimeoutError:
            self._take_break(self.cfg.sleep_timeout, "Page has timed out. Taking a long break!")
            return


        # Sleep for a certain amount of time
        if "www.google.com" in url:
            self._sleep(self.cfg.sleep_google_search, "Google Search")
        else:
            self._sleep(self.cfg.sleep_linkedin, "Linkedin Profile")


        # Check that linkedin didn't rate limit us
        if "Join to view full profiles for free" in html:
            self._take_break(self.cfg.sleep_rate_limiting, "Linkeding is rate-limiting us. Taking a break.")
            return None


        return html

    def _sleep(self, interval, reason):
        """
        A sleep helper function that prints the reason its sleeping, and the random interval of sleep
        :param interval: A tuple (mintime, maxtime)
        :param reason: Why the sleep is happening (for a pretty print)
        """

        # TODO: Add a self.browser.back() or something here to fake human use, and/or self.browser.delete_all_cookies()
        rand_interval = uniform(*interval)
        print("Sleeping", rand_interval, "seconds: ", reason)

        # If the browser isn't open, do a normal sleep
        if self.browser is None:
            sleep(rand_interval)
            return

        # If the browser is closed, sleep halfway then do a random action, then continue sleeping
        sleep(rand_interval / 2)

        # Do a random action while sleeping
        actions = [self.browser.back,
                   lambda: self.browser.set_window_size(randint(700, 1080), randint(700, 1080)),
                   lambda: self.browser.set_window_position(randint(0, 300), randint(0, 300)),
                   self.browser.maximize_window,
                   self.browser.delete_all_cookies]

        action = choice(actions)
        print("Performing random action: ", action)
        action()
        sleep(rand_interval / 2)

    def _take_break(self, break_interval, reason):
        """ Shut down browser, restart with new browser """
        self._close_browser()
        self._sleep(break_interval, reason)
        self.profiles_since_break = 0
        self._start_browser()


    def _close_browser(self):
        self.browser.quit()
        self.browser = None

    def _start_browser(self):
        assert self.browser is None, "Browser must not exist in order to call _start_browser!"

        # Load a user profile from normal chrome
        user_profile = "C:\\Users\\Alex Thiel\\AppData\\Local\\Google\\Chrome\\User Data\\Default"

        # Options
        options = Options()
        options.add_argument("user-data-dir={}".format(user_profile))
        options.add_experimental_option(
                            "excludeSwitches",
                            ["ignore-certificate-errors",
                             "safebrowsing-disable-download-protection",
                             "safebrowsing-disable-auto-update",
                             "disable-client-side-phishing-detection"])
        os.environ["webdriver.chrome.driver"] = self.driver_path

        # Add variation to the browser
        if randint(0, 2) == 1:
            options.add_argument("--incognito")
            print("Option: Incognito")
        if randint(0, 2) == 1:
            options.add_argument("--disable-extensions")
            print("Option: Disabling Extensions")
        if randint(0, 2) == 1:
            options.add_argument("--disable-plugins-discovery")
            print("Option: Disabling plugins discovery")
        if randint(0, 2) == 1:
            options.add_argument('--no-referrers')
            print("Option: No Referrers")
        if randint(0, 2) == 1:
            options.add_argument('--disable-web-security')
            print("Option: Disabled web security")
        if randint(0, 2) == 1:
            options.add_argument('--allow-running-insecure-content')
            print("Option: Allowing running insecure content")
        if randint(0, 2) == 1:
            options.add_experimental_option('prefs', {
                'credentials_enable_service': False,
                'profile': {'password_manager_enabled': False}
            })
            print("Options: Disabled Password Manager")

        # options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})

        agent = UserAgent().random
        options.add_argument("user-agent=" + agent)
        self.current_agent = agent
        print("Option: Agent:", agent)

        # Open up browser window
        self.browser = Driver(executable_path=self.driver_path, chrome_options=options)
        self.browser.set_page_load_timeout(self.cfg.browser_timeout)
        self.browser.delete_all_cookies()

        if randint(0, 2) == 1:
            print("Option: Start Maximized")
            self.browser.maximize_window()
        else:
            self.browser.set_window_size(randint(700, 1080), randint(700, 1080))
            self.browser.set_window_position(randint(0, 300), randint(0, 300))


if __name__ == "__main__":
    from linkedin.profile_manager import ProfileManager
    from crawling.config import CrawlerConfig

    # Get the list of websites from the file
    website_list = []
    with open("Websites.txt", "r") as file:
        for line in file:
            line = line.replace('\n', '')
            website_list.append(line)

    # Open existing profiles
    profile_manager = ProfileManager("../ScrapedProfiles")

    config = CrawlerConfig()

    # Run the crawler
    crawler = Crawler(profile_manager=profile_manager,
                      driver_path="../Resources/chromedriver.exe",
                      config=config)
    crawler.run()




