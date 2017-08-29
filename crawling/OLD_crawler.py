"""Contains an implementation of a web crawler for finding image URLs.
"""
from urllib.parse import urlparse
from selenium.webdriver import PhantomJS as Driver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from threading import Thread, Timer
from urllib.error import URLError
import paths
import cv2
import numpy as np
import queue
import urllib


def _same_domain(url1, url2):
    """Returns true if the two domains have the same domain.
    :return: true if domains are the same
    """
    return urlparse(url1).netloc == urlparse(url2).netloc


class Crawler(Thread):
    """A basic web crawler that looks for image URLs recursively.
    """

    def __init__(self, website_list, max_depth, max_browser_instances, load_timeout):
        """Creates a new web crawler.

        :param website_list: The list of web URLs to start crawling from
        :param max_depth: The maximum amount of pages deep the crawl should go
        :param max_browser_instances: The maximum amount of browser instances
            that may be open at once
        """

        super(Crawler, self).__init__()

        # A value from 0 to 100 showing how complete the crawl is.
        self.progress = 0
        self.scraped_page_cnt = 0
        self.failed_page_cnt = 0


        self.__running = False
        self.__results = queue.Queue()

        self.__website_list = website_list
        self.__browser_pool = queue.Queue()
        self.__crawled_urls = []
        self.__found_image_urls = []
        self.__max_depth = max_depth
        self.__load_timeout = load_timeout
        self.__browser_instance_cnt = max_browser_instances
        self.__browser_close_methods = []
        self.__is_finished = False


    def run(self):
        """Starts the crawling process the listed websites. The results queue
        will start filling up with image URLs.
        """
        self.__running = True

        # Open up all browser windows
        for i in range(self.__browser_instance_cnt):
            if not self.__running:
                break # End prematurely

            browser = Driver(executable_path=paths.driver)

            # Set up the browser to be closable
            self.__browser_close_methods.append(browser.quit)

            # Set the page timeout
            browser.set_page_load_timeout(self.__load_timeout)
            self.__browser_pool.put(browser)

        crawl_threads = []

        # Starts crawling the page and returns the given browser to the pool
        # when finished
        def crawl_and_return_to_pool(url, browser):
            progress_weight = (1 / len(self.__website_list)) * 100
            self._crawl_page(url, browser, progress_weight)
            self.__browser_pool.put(browser)

        # Start crawling each URL
        for url in self.__website_list:
            if not self.__running:
                break # End prematurely

            # Wait for an unused browser instance
            browser = self.__browser_pool.get()
            # Start crawling
            thread = Thread(target = crawl_and_return_to_pool, args = (url, browser))
            thread.start()
            crawl_threads.append(thread)

        # Wait for crawling to finish
        for thread in crawl_threads:
            thread.join()

        self._close_browsers()

        self.__running = False
        self.__is_finished = True


    def get_image(self):
        """Returns image data loaded from the crawler. Blocks until a new image
        has been found or until the crawler has finished running, in which case
        None is returned.

        :return: A tuple with image as a Numpy array and the URL of the page it
        came from, or None
        """

        if self.__running:
            try:
                # Load image from URL and convert it to a Numpy array
                (url, page_url) = self.__results.get_nowait()
                image = self._url_to_image(url)
                if image is None:
                    return None, None
                return self._url_to_image(url), page_url
            except queue.Empty:
                # Try again
                pass

        return None, None

    def is_finished(self):
        """Returns true if the scraping job is finished.
        :return: True if scraping is finished
        """
        return self.__is_finished

    def _crawl_page(self, url, browser, progress_step, depth=0):
        """Crawls the given page for images and links to other webpages. Image
        URLs are put in the results queue. Links are followed and crawled.

        :param url: The URL of the page to crawl
        :param browser: The browser instance to open the page on
        :param progress_step: The amount to increment progress after this step
        is finished
        :param depth: The current crawling depth, starting at zero
        """

        if depth > self.__max_depth:
            self.progress += progress_step
            return
        if not self.__running:
            # Abort processing the page
            return

        self.__crawled_urls.append(url)

        image_urls = []
        link_urls = []

        # Load up the page
        try:
            browser.get(url)

            image_urls = self._get_image_urls(browser)
            link_urls = self._get_link_urls(browser)

            # Emit the URLs of all unique images in the page
            for image_url in image_urls:
                if image_url not in self.__found_image_urls:
                    self.__results.put((image_url, url))
                    self.__found_image_urls.append(image_url)

            # Follow links to unique URLs that have the same domain as the parent
            for link_url in link_urls:
                if link_url not in self.__crawled_urls and _same_domain(url, link_url):
                    # Split up the parent's progress step value by the value of a
                    # single link
                    next_progress_step = (1 / len(link_urls)) * progress_step
                    self._crawl_page(link_url, browser, next_progress_step, depth=depth+1)
        except TimeoutException:
            self.failed_page_cnt += 1
            print("Warning: page " + url + " timed out")
        except URLError:
            self.failed_page_cnt
            print("Warning: page " + url + " refused connection")

        self.scraped_page_cnt += 1


    def _get_image_urls(self, browser):
        """Returns the URLs of all images in the current page.

        :param browser: The browser that the page is loaded on
        :return: list of image URLs
        """

        images = browser.find_elements_by_css_selector("img")
        urls = []
        for image in images:
            try:
                new_url = image.get_attribute("src")  # Throws error sometimes
                if new_url is not None:
                    urls.append(new_url)
            except StaleElementReferenceException as e:
                print("ERROR: Tried to get a URL that has already disappeared from page", e)
        return urls


    def _get_link_urls(self, browser):
        """Returns the URLs of all links in the current page.

        :param browser: The browser that the page is loaded on
        :return: list of link URLs
        """
        urls = []

        # OLD METHOD: Opens tons of sockets and causes failures in windows
        links = browser.find_elements_by_css_selector("a")
        for link in links:
            try:
                new_url = link.get_attribute("href")
                urls.append(new_url)
            except StaleElementReferenceException as e:
                print("Error; Unable to get a link attribute: ", e)

        return urls


    def _url_to_image(self, url):
        """ Download the image, convert it to a NumPy array, and then read it into OpenCV format"""
        # image_data = urllib.request.urlopen(url).read()
        # return np.array(Image.open(io.BytesIO(image_data)))

        try:
            resp = urllib.request.urlopen(url, timeout=self.__load_timeout)
        except URLError as e:
            print("Error: Could not get image from: ", url, " because: ", e)
            return None
        except ValueError as e:
            print("Error: Tried to open a URL that had a length of zero",e)
            return None
        except ConnectionAbortedError as e:
            print("Error: Computer lost internet connection", e)
        except Exception as e:
            print("URL Before crash: ", url)
            raise

        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        if len(image):
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            return image
        else:
            return None

    def _close_browsers(self):
        """Closes all browser instances."""
        for cl in self.__browser_close_methods:
            print("closing a browser...")
            cl()
            print("Done")

    def close(self):
        """Prematurely stops crawling pages.
        """
        self.__running = False
        self._close_browsers()
