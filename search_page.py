from RPA.Browser.Selenium import Selenium
from urllib.parse import urlparse, urlunparse
import re
import constants as const
from logger import logger
from article import Article


class SearchPage:

    def __init__(self, browser_lib: Selenium):
        self.browser_lib = browser_lib

    def set_date_range(self, start_date, end_date):
        logger.info('Set date range')

        # Define selectors.
        search_date_dropdown_selector = 'css:[data-testid="search-date-dropdown-a"]'
        specific_dates_selector = 'css:[value="Specific Dates"]'
        start_date_selector = 'css:[data-testid="DateRange-startDate"]'
        end_date_selector = 'css:[data-testid="DateRange-endDate"]'
        date_range_selector = 'css:div.query-facet-date button[facet-name="date"]'

        # Navigate to date range picker.
        self.browser_lib.click_element(search_date_dropdown_selector)
        self.browser_lib.click_element(specific_dates_selector)

        # Get date strings in appropriate format.
        start_date_string = start_date.strftime(const.DATE_INPUT_FORMAT)
        end_date_string = end_date.strftime(const.DATE_INPUT_FORMAT)

        # Set dates.
        self.browser_lib.input_text(
            start_date_selector, start_date_string
        )
        self.browser_lib.input_text(
            end_date_selector, end_date_string)
        self.browser_lib.press_keys(end_date_selector, "ENTER")
        self.browser_lib.reload_page()

        # Validate.
        date_range_value = self.browser_lib.get_element_attribute(
            date_range_selector, 'value')
        parsed_start_date = re.search(
            r"^\d{2}/\d{2}/\d{4}", date_range_value).group()
        parsed_end_date = re.search(
            r"\d{2}/\d{2}/\d{4}$", date_range_value).group()
        assert start_date_string == parsed_start_date and end_date_string == parsed_end_date,\
            "Date range from UI doesn't match"

    def set_filters(self, items, filter_type):
        # Arguments validation.
        assert filter_type in [
            'type', 'section'], f"Undefined filter type: {filter_type}"
        filter_name = 'sections' if filter_type == 'section' else 'categories'
        if len(items) == 0:
            logger.info(f"No {filter_name} filter provided")
            return
        if "any" in items:
            logger.warning(f"{filter_name} contain `Any`. Skipping selection.")
            return

        logger.info(
            f"Set {filter_name}")

        # Define selectors.
        form_selector = f'css:[role="form"][data-testid="{filter_type}"]'
        button_selector = 'css:button[data-testid="search-multiselect-button"]'
        dropdown_list_selector = 'css:[data-testid="multi-select-dropdown-list"]'
        checkbox_selector = 'css:input[type="checkbox"]'
        selected_item_selector = f'css:div.query-facet-{filter_type}s button[facet-name="{filter_type}s"]'

        # Open dropdown list.
        type_form_element = self.browser_lib.find_element(form_selector)
        button_element = self.browser_lib.find_element(
            button_selector, type_form_element)
        self.browser_lib.click_element(button_element)

        # Find all checkbox elements and map it by value.
        dropdown_list_element = self.browser_lib.find_element(
            dropdown_list_selector, type_form_element)
        checkbox_elements = self.browser_lib.find_elements(
            checkbox_selector, dropdown_list_element)
        checkbox_by_value = {}
        for checkbox in checkbox_elements:
            checkbox_value = self.browser_lib.get_element_attribute(
                checkbox, 'value')
            formatted_value = checkbox_value.split(
                '|nyt:', 1)[0].replace(" ", "").lower()
            checkbox_by_value[formatted_value] = checkbox

        # Select items.
        not_found_items = []
        for item in items:
            try:
                self.browser_lib.click_element(
                    checkbox_by_value[item])
            except Exception as e:
                logger.warning(f"Unknown {filter_name}: {e}")
                not_found_items.append(item)

        # Verify selected items.
        selected_item_elements = self.browser_lib.find_elements(
            selected_item_selector)
        selected_items_labels = set()
        for element in selected_item_elements:
            value = self.browser_lib.get_element_attribute(element, 'value')
            formatted_value = value.split(
                '|nyt:', 1)[0].replace(" ", "").lower()
            selected_items_labels.add(formatted_value)

        expected_selected_items = items.difference(not_found_items)
        assert len(expected_selected_items.difference(
            selected_items_labels)) == 0, f"Selected {type} items don't match"

    def sort_by_newest(self):
        logger.info("Sort by newest")

        # Define selectors.
        sort_by_selector = 'css:[data-testid="SearchForm-sortBy"]'

        # Select.
        value_to_select = 'newest'
        self.browser_lib.select_from_list_by_value(
            sort_by_selector, value_to_select)

        # Verify.
        sort_by_element_value = self.browser_lib.get_selected_list_value(
            sort_by_selector)
        assert sort_by_element_value == value_to_select

    def expand_and_get_all_articles(self):
        logger.info("Expand all articles")

        # Define selectors.
        show_more_button_selector = 'css:[data-testid="search-show-more-button"]'
        search_results_selector = 'css:[data-testid="search-results"]'
        search_result_selector = 'css:[data-testid="search-bodega-result"]'
        search_result_link_selector = 'css:[data-testid="search-bodega-result"] a'

        # Expand all elements.
        while self.browser_lib.is_element_enabled(show_more_button_selector):
            try:
                self.browser_lib.scroll_element_into_view(
                    show_more_button_selector)
                self.browser_lib.click_element(show_more_button_selector)
            except Exception as e:
                logger.info(f"No more Show Button - {e}")
                break
        self.browser_lib.wait_until_element_is_enabled(
            search_results_selector, timeout=10
        )

        # Get all elements.
        search_result_items = self.browser_lib.find_elements(
            search_result_selector
        )
        logger.info(f"All articles count: {len(search_result_items)}")

        # Get unique elements using articles url as a dictionary key.
        elements_by_url = dict()
        for element in search_result_items:
            link_element = self.browser_lib.find_element(
                search_result_link_selector, element)
            link_url = self.browser_lib.get_element_attribute(
                link_element, 'href')
            url_without_parameters = self.__get_clean_url(link_url)
            elements_by_url[url_without_parameters] = element

        unique_elements = elements_by_url.values()
        logger.info(f"Unique articles count: {len(unique_elements)}")
        return unique_elements

    def parse_articles_data(self, article_elements, search_phrase):
        logger.info("Parse articles data")
        data = []
        for element in article_elements:
            try:
                article = Article(self.browser_lib, element, search_phrase)
                data.append(article)
            except Exception as e:
                logger.warning(
                    f"Failed to parse article's data: {e}")
        return data

    # Helper Methods.

    @staticmethod
    def __get_clean_url(url_string) -> str:
        return urlunparse(list(urlparse(url_string)[:3]) + ['', '', ''])
