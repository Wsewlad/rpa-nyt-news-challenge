from RPA.Browser.Selenium import Selenium
import constants as const
from logger import logger


class HomePage:

    def __init__(self, browser_lib: Selenium):
        self.browser_lib = browser_lib

    def lend_first_page(self):
        # Define selectors
        accept_cookies_selector = "//button[text()='Accept']"

        self.browser_lib.open_available_browser(const.BASE_URL)
        self.browser_lib.set_window_size(1920, 1080)
        title = self.browser_lib.get_title()

        if self.browser_lib.is_element_visible(accept_cookies_selector):
            logger.info('Cookies popup found. Closing...')
            self.browser_lib.click_element(accept_cookies_selector)

        assert title == "The New York Times - Breaking News, US News, World News and Videos", "This is not Home Page, current page is - " + \
            self.browser_lib.get_location()

    def enter_search_query(self, query):
        logger.info('Enter search query')
        # Define selectors
        search_button = 'css:[data-test-id="search-button"]'
        search_input = 'css:[data-testid="search-input"]'
        search_submit = 'css:[data-test-id="search-submit"]'
        search_text_field = 'searchTextField'

        # Type search query
        self.browser_lib.click_element(search_button)
        self.browser_lib.input_text_when_element_is_visible(
            search_input, query
        )
        self.browser_lib.click_element(search_submit)

        # Validate applied search query on the search page
        self.browser_lib.wait_until_page_contains_element(search_text_field)
        search_text_field_value = self.browser_lib.get_element_attribute(
            search_text_field, 'value'
        )
        search_text_field_matched = self.browser_lib.is_element_attribute_equal_to(
            search_text_field, 'value', query
        )

        assert search_text_field_matched, f"Search text field value [{search_text_field_value}] doesn't match the query [{query}]"
