from threading import Thread
from selenium.webdriver import Chrome as Driver
from bs4 import BeautifulSoup
import queue


class Crawler:
    def __init__(self, profile_manager, driver_path, website_list, **options):
        """

        :param website_list: A list of URL's that should be 'seeds' for finding linkedin profiles
        :param driver_path: The path to the browser driver that is being used for scraping
        :param browser_timeout: How long a browser will wait (in seconds) before giving up and trying a new URL
        :param max_browsers: How many browsers can be open and scraping at once. TOO MANY AND MAY BE IP BANNED
        :param max_depth: How many links deep the crawler will go into a URL from the website_list
        :param min_wait_time: How many seconds to wait between requests
        """
        super().__init__()


        # Options
        self.__browser_instance_cnt = options.get("max_browsers", 1)
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
        self.__browser_pool = queue.Queue()
        self.__browser_close_methods = []


    def run(self):
        """ This runs in a new thread when crawler.run() is called """

        self.__running = True

        # Open up all browser windows
        for i in range(self.__browser_instance_cnt):
            if not self.__running: break  # End prematurely

            browser = Driver(executable_path=self.__driver_path)

            # Save the close method for later use
            self.__browser_close_methods.append(browser.quit)

            # Set the page timeout
            browser.set_page_load_timeout(self.__browser_timeout)
            self.__browser_pool.put(browser)

        crawl_threads = []

        # Start crawling the pages and return the given browser to the pool when finished
        def crawl_and_return_to_pool(url, browser):
            self._crawl_page(url, browser)
            self.__browser_pool.put(browser)

        # Start crawling each URL
        print("Going through url in",  self.__website_list)
        for url in self.__website_list:
            if not self.__running: break  # End prematurely

            # Wait for an unused browser instance
            browser = self.__browser_pool.get()

            # Start crawling
            thread = Thread(target = crawl_and_return_to_pool, args=(url, browser))
            thread.start()
            crawl_threads.append(thread)

        # Wait for crawling to finish
        for thread in crawl_threads:
            thread.join()

        self._close_browsers()
        self.__running = False

    def _crawl_page(self, url, browser, depth=0):
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
            print("ERROR: Tried to crawl the same URL twice: ", url)
        self.__crawled_urls.append(url)



        # If it is a linkedin profile currently being crawled, save the HTML
        if "linkedin" in url and "/in/" in url and url.count("/") == 4:

            # Check that this profile has not been parsed before
            username = url.split("/in/", 1)[1]
            if username in self.__profile_manager.users:
                print("Tried to analyze", username, "when it was already scraped!")
                return
            print("Analyzing: ", url, username)

            # Load the page
            print("Sleeping...")
            sleep(self.__min_wait_time)
            browser.get(url)
            html = browser.page_source

            # Save HTML to a file
            self.__profile_manager.write_new(html)

            return

        elif "www.google.com" in url:
            # Load the page
            print("Sleeping...")
            sleep(self.__min_wait_time)
            browser.get(url)
            html = browser.page_source

            # If it is a google search page currently being crawled to find more linkedin profiles
            linkedin_urls = self._get_results_urls(html)
            for url in linkedin_urls:
                self._crawl_page(url, browser, depth=depth + 1)
        else:
            print("ERROR: Tried to crawl url: ", url)

    def _close_browsers(self):
        """ Tries to close all open browsers. """
        """ Close all open browsers """
        for closer in self.__browser_close_methods:
            print("Closing a browser... ", end="")
            closer()
            print("Done")


    def _get_results_urls(self, html):
        # Get links to results from a google search
        links = []
        soup = BeautifulSoup(html, "html5lib")

        for link in soup.find_all('cite', class_="_Rm"):
            links.append(link.text)

        return links


if __name__ == "__main__":
    from time import sleep
    import os

    from linkedin.profile_manager import ProfileManager
    import config

    profile_manager = ProfileManager("../ScrapedProfiles")

    config = config.Config("Websites.txt", "crawler_settings.json")
    crawler = Crawler(profile_manager=profile_manager,
                      driver_path="../Resources/chromedriver.exe",
                      website_list=config.websites,
                      browser_timeout=config.browser_timeout,
                      max_browsers=config.max_browser_instances,
                      max_depth=config.max_depth)
    crawler.run()




