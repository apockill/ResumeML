from time import sleep
from urllib.parse import urljoin
from random import uniform, randint, shuffle, choice
import os

from selenium.webdriver import Chrome as Driver
from selenium.webdriver import ChromeOptions as Options
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, profile_manager, driver_path, website_list, **options):
        """

        :param website_list: A list of URL's that should be 'seeds' for finding linkedin profiles
        :param driver_path: The path to the browser driver that is being used for scraping
        :param browser_timeout: How long a browser will wait (in seconds) before giving up and trying a new URL
        :param min_wait_time: How many seconds to wait between requests
        :param max_urls_between_break: How many profiles can be crawled before the program takes a break
        """
        super().__init__()


        # Options
        self.__browser_timeout = options.get("browser_timeout", 30)
        self.__min_wait_time = options.get("min_wait_time", 3)  # Time
        self.__max_urls_between_break = options.get("max_urls_between_break", 50)  # URLS crawled since a restart

        # Parameters
        self.__driver_path = driver_path
        self.__website_list = website_list
        self.__profiles_since_break = 0

        # Controls
        self.__profile_manager = profile_manager
        self.__crawled_urls = []
        self.__running = False
        self.__browser = None
        self.__browser_close_methods = []

    def run(self):
        """ This runs in a new thread when crawler.run() is called """

        self.__running = True

        self._restart_browser()


        # Start crawling each URL
        for url in self.__website_list:
            if not self.__running: break  # End prematurely
            print("Starting Crawling on Seed: ", url)
            self._crawl_page(url)

        self.__browser.quit()
        self.__browser = None
        self.__running = False

    def _crawl_page(self, url, depth=0):
        """
        If the url is a linkedin url, it will check if it is a profile, save it, and add it to crawled URL's.

        If the url is NOT a linkedin url (thus a google search page), it will find linkedin URL's and crawl them.
        It will also find "next search page" arrows on google, and crawl those as well.

        :param url: The link to crawl
        :param browser: What browser object will open and render the link
        :param depth: How many links deep the searcher will go
        :return:
        """

        if not self.__running: return  # End prematurely

        if url in self.__crawled_urls:
            print("Tried to crawl the same URL twice", url)
            return
        self.__crawled_urls.append(url)

        if self.__profiles_since_break > self.__max_urls_between_break - randint(0, 2):
            print("Crawled", self.__profiles_since_break, "urls since the last restart, time to take a quick break!")
            self.__browser.quit()
            self.__browser = None
            rand_sleep = uniform(30, 90)
            print("Sleeping ", rand_sleep, "seconds for a break!")
            sleep(rand_sleep)
            self.__profiles_since_break = 0
            self._restart_browser()


        # If it is a linkedin profile currently being crawled, save the HTML
        if "linkedin" in url and "/in/" in url and url.count("/") == 4:

            # Check that this profile has not been parsed before
            username = url.split("/in/", 1)[1]
            if username in self.__profile_manager.users:
                print("Skipped analyzing ", username, "because it was already scraped!")
                return
            print("Analyzing #", len(self.__profile_manager), url, username)

            # Load the page
            html = self._load_page(url)
            self.__profiles_since_break += 1

            # If linkedin rate-limited us, continue to the next profile
            if html is None: return

            # Save HTML to a file
            try:
                self.__profile_manager.write_new(html)
            except Exception as e:
                print("ERROR: While saving HTML: ", e, " in url: ", url)  # TODO: Fix this

            # Try to prevent rate limiting
            self.__browser.delete_all_cookies()
        elif "www.google.com" in url:
            # Load the page
            html = self._load_page(url)

            # If it is a google search page currently being crawled to find more linkedin profiles
            linkedin_urls = self._get_results_urls(html)
            shuffle(linkedin_urls)  # Makes it harder to be tracked
            for url in linkedin_urls:
                self._crawl_page(url, depth=depth + 1)

            # Get the "Next" link to go to the next page of results
            soup = BeautifulSoup(html, "lxml")
            next_link = soup.find("a", {"id": "pnnext"})
            if next_link is not None:
                next_link = urljoin("http://www.google.com", next_link["href"])
                self._crawl_page(next_link, depth=depth + 1)
        else:
            print("ERROR: Tried to crawl url: ", url)

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
            self.__browser.get(url)
        except TimeoutError:
            print("ERROR: Page has timed out. Taking a long break of 200 seconds")
            self.__browser.quit()
            self.__browser = None
            sleep(200)
            self._restart_browser()
            
        html = self.__browser.page_source

        # Sleep for a certain amount of time
        if "www.google.com" in url:
            rand_sleep = randint(1, 3)
            print("Sleeping", rand_sleep, "seconds between Google Searches...")
            sleep(rand_sleep)
        else:
            rand_sleep = randint(self.__min_wait_time, self.__min_wait_time * 2)
            print("Sleeping", rand_sleep, "seconds between profiles")
            sleep(rand_sleep / 2.0)
            self.__browser.back()
            sleep(rand_sleep / 2.0)


        # Check that linkedin didn't rate limit us
        if "Join to view full profiles for free" in html:
            print("ERROR: Linkedin is rate-limiting us. Closing Browser...")
            self._restart_browser()
            return None

        if randint(0, 5) == 0:
            self.__browser.delete_all_cookies()
        return html

    def _restart_browser(self):

        if self.__browser is not None:
            self.__browser.quit()
            self.__browser = None
            rand_sleep = uniform(60, 120)
            print("Sleeping", rand_sleep, "seconds between browser restart...")
            sleep(rand_sleep)

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
        os.environ["webdriver.chrome.driver"] = self.__driver_path

        # Add variation to the browser
        if randint(0, 1):
            options.add_argument("--incognito")
            print("Option: Incognito")
        if randint(0, 1):
            options.add_argument("--disable-extensions")
            print("Option: Disabling Extensions")
        if randint(0, 1):
            options.add_argument("--disable-plugins-discovery")
            print("Option: Disabling plugins discovery")
        if randint(0, 1):
            options.add_argument("--start-maximized")
            print("Option: Starting maximized")

        possible_agents = [None,
             # Most recent user agents
             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
             "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36",
             "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:34.0) Gecko/20100101 Firefox/34.0",
             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
             "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/5.0)",
             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.112 Safari/535.1",
             "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
             "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
             # Most popular user agents
             "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.6.01001)",
             "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.7.01001)",
             "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.5.01003)",
             "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0",
             "Mozilla/5.0 (Windows NT 5.1; rv:13.0) Gecko/20100101 Firefox/13.0.1",
             "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0",
             "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.0.3705)",
             "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0.1",
             "Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.01",

             # Old, possibly bad user agents
             "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
             "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
             "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13",
             "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
             "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
             "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36",
             "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_7) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"]

        """ BAD
        "Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
        
        """
        agent = choice(possible_agents)
        if agent is not None:
            options.add_argument("user-agent=" + agent)
        print("Option: Agent", agent)

        # Open up browser window
        self.__browser = Driver(executable_path=self.__driver_path, chrome_options=options)
        self.__browser.set_page_load_timeout(self.__browser_timeout)
        self.__browser.delete_all_cookies()
        self.__browser.set_window_size(randint(700, 1080), randint(700, 1080))
        self.__browser.set_window_position(randint(0, 300), randint(0, 300))


        # print("Opened new browser in ip: ", self.__browser.get("http://whatismyipaddress.com"))

if __name__ == "__main__":
    from linkedin.profile_manager import ProfileManager

    # Get the list of websites from the file
    website_list = []
    with open("Websites.txt", "r") as file:
        for line in file:
            line = line.replace('\n', '')
            website_list.append(line)

    # Open existing profiles
    profile_manager = ProfileManager("../ScrapedProfiles")


    # config = config.Config("Websites.txt", "crawler_settings.json")
    # Run the crawler
    crawler = Crawler(profile_manager=profile_manager,
                      driver_path="../Resources/chromedriver.exe",
                      website_list=website_list,
                      browser_timeout=30,
                      min_wait_time=10,
                      max_urls_between_break=15)
    crawler.run()




