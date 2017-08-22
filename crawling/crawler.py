from threading import Thread
from selenium.webdriver import PhantomJS as Driver
import queue


class Crawler(Thread):
    def __init__(self, website_list, driver_path, browser_timeout, max_browser_instances, max_depth):
        """

        :param website_list: A list of URL's that should be 'seeds' for finding linkedin profiles
        :param driver_path: The path to the browser driver that is being used for scraping
        :param browser_timeout: How long a browser will wait (in seconds) before giving up and trying a new URL
        :param max_browser_instances: How many browsers can be open and scraping at once. TOO MANY AND MAY BE IP BANNED
        :param max_depth: How many links deep the crawler will go into a URL from the website_list
        """
        super().__init__()

        # Parameters
        self.__driver_path = driver_path
        self.__browser_instance_cnt = max_browser_instances
        self.__browser_timeout = browser_timeout
        self.__website_list = website_list
        self.__max_depth = max_depth

        # Controls
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

    def close(self):
        """ Tries to close all browsers and threads quickly. Only call from the main thread or a parent thread. """
        self.__running = False
        self._close_browsers()
        self.join(2)

    def _crawl_page(self, url, browser, depth=0):
        if depth > self.__max_depth:
            print("Hit max depth")
            return
        if not self.__running: return  # End prematurely

        self.__crawled_urls.append(url)


    def _close_browsers(self):
        """ Tries to close all open browsers. """
        """ Close all open browsers """
        for closer in self.__browser_close_methods:
            print("Closing a browser...",end="")
            closer()
            print("Done")
            self.__browser_close_methods.pop(0)




if __name__ == "__main__":
    from time import sleep
    import config
    config = config.Config("Websites.txt", "crawler_settings.json")
    crawler = Crawler(driver_path="../Resources/phantomjs.exe",
                      website_list=config.websites,
                      browser_timeout=config.browser_timeout,
                      max_browser_instances=config.max_browser_instances,
                      max_depth=config.max_depth)
    crawler.start()

    sleep(5)
    print("Closing Program")
    crawler.close()