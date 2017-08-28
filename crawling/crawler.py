from threading import Thread
from time import sleep
from urllib.parse import urljoin
from random import randrange
import queue

from selenium.webdriver import Chrome as Driver
from selenium.webdriver import ChromeOptions as Options
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, profile_manager, driver_path, website_list, **options):
        """

        :param website_list: A list of URL's that should be 'seeds' for finding linkedin profiles
        :param driver_path: The path to the browser driver that is being used for scraping
        :param browser_timeout: How long a browser will wait (in seconds) before giving up and trying a new URL
        :param max_depth: How many links deep the crawler will go into a URL from the website_list
        :param min_wait_time: How many seconds to wait between requests
        """
        super().__init__()


        # Options
        self.__browser_timeout = options.get("browser_timeout", 30)
        self.__max_depth = options.get("max_depth", 1)
        self.__min_wait_time = options.get("min_wait_time", 3)  # Time

        # Parameters
        self.__driver_path = driver_path
        self.__website_list = website_list


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

        if depth > self.__max_depth:
            print("Hit max depth")
            return

        if not self.__running: return  # End prematurely

        if url in self.__crawled_urls:
            print("Tried to crawl the same URL twice", url)
            return
        self.__crawled_urls.append(url)



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

            # If linkedin rate-limited us, continue to the next profile
            if html is None: return

            # Save HTML to a file
            self.__profile_manager.write_new(html)

        elif "www.google.com" in url:
            # Load the page
            html = self._load_page(url)

            # If it is a google search page currently being crawled to find more linkedin profiles
            linkedin_urls = self._get_results_urls(html)
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
        self.__browser.get(url)

        # Sleep for a certain amount of time

        if "www.google.com" in url:
            rand_sleep = randrange(1, 3, 1)
            print("Sleeping", rand_sleep, "seconds between Google Searches...")
            sleep(rand_sleep)
        else:
            rand_sleep = randrange(self.__min_wait_time, self.__min_wait_time * 2, 1)
            print("Sleeping", rand_sleep, "seconds between profiles")
            sleep(rand_sleep)
        html = self.__browser.page_source

        # Check that linkedin didn't rate limit us
        if "Join to view full profiles for free" in html:
            print("ERROR: Linkedin is rate-limiting us. Closing Browser...")
            self._restart_browser()
            return None
        return html

    def _restart_browser(self):

        if self.__browser is not None:
            self.__browser.quit()
            self.__browser = None
            rand_sleep = randrange(50, 75, 1)
            print("Sleeping", rand_sleep, "seconds between browser restart...")
            sleep(rand_sleep)

        # Options
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0a2) Gecko/20111101 Firefox/9.0a2")

        # Open up browser window
        self.__browser = Driver(executable_path=self.__driver_path, chrome_options=options)
        self.__browser.set_page_load_timeout(self.__browser_timeout)

        agent = self.__browser.execute_script("return navigator.userAgent")
        print("User Agent: ", agent)
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
                      max_depth=15,
                      min_wait_time=10)
    crawler.run()




