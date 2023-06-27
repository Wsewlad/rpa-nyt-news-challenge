from RPA.Browser.Selenium import Selenium
from urllib.parse import urlparse, parse_qs, urlunparse
import re
import constants as const
from logger import logger
from article import Article


class SearchPage:

    def __init__(self, browser_lib: Selenium):
        self.browser_lib = browser_lib
        title = self.browser_lib.get_title()
        assert title == "The New York Times - Search", "This is not Search Page, current page is - " + \
            self.browser_lib.get_location()

    def set_date_range(self, start_date, end_date):
        logger.info('Set date range')
        # Define selectors
        search_date_dropdown_selector = 'css:[data-testid="search-date-dropdown-a"]'
        specific_dates_selector = 'css:[value="Specific Dates"]'
        date_range_start_date_selector = 'css:[data-testid="DateRange-startDate"]'
        date_range_end_date_selector = 'css:[data-testid="DateRange-endDate"]'
        # Navigate to date range picker
        self.browser_lib.click_element(search_date_dropdown_selector)
        self.browser_lib.click_element(specific_dates_selector)
        # Get date strings in appropriate format
        start_date_input_string = start_date.strftime(const.DATE_INPUT_FORMAT)
        end_date_input_string = end_date.strftime(const.DATE_INPUT_FORMAT)
        # Input dates
        self.browser_lib.input_text(
            date_range_start_date_selector, start_date_input_string
        )
        self.browser_lib.input_text(
            date_range_end_date_selector, end_date_input_string)
        self.browser_lib.press_keys(date_range_end_date_selector, "ENTER")
        # Validate date range from UI
        matched = self.__parse_and_verify_date_range_from_ui(
            start_date_input_string, end_date_input_string)
        if not matched:
            self.browser_lib.reload_page()
        matched = self.__parse_and_verify_date_range_from_ui(
            start_date_input_string, end_date_input_string)
        assert matched, "Date range from UI doesn't match"

    def set_filters(self, items, filter_type):
        if filter_type not in ['type', 'section']:
            raise Exception(f"Undefined filter type: {filter_type}")

        filter = 'sections' if filter_type == 'section' else 'categories'
        if len(items) == 0:
            logger.info(f"No {filter} filter provided")

        logger.info(
            f"Set {filter}")

        # Define selectors
        form_selector = f'css:[role="form"][data-testid="{filter_type}"]'
        button_selector = 'css:button[data-testid="search-multiselect-button"]'
        dropdown_list_selector = 'css:[data-testid="multi-select-dropdown-list"]'
        checkbox_selector = 'css:input[type="checkbox"]'

        # Open dropdown list
        type_form_element = self.browser_lib.find_element(form_selector)
        button_element = self.browser_lib.find_element(
            button_selector, type_form_element)
        self.browser_lib.click_element(button_element)

        # Wait for dropdown list
        dropdown_list_element = self.browser_lib.find_element(
            dropdown_list_selector, type_form_element)
        self.browser_lib.wait_until_element_is_visible(dropdown_list_element)

        # Find all checkbox elements and map it by value
        checkbox_elements = self.browser_lib.find_elements(
            checkbox_selector, dropdown_list_element)
        checkbox_by_value = dict([
            (
                self.__format_item(
                    self.browser_lib.get_element_attribute(
                        checkbox, 'value'
                    ).split('|nyt:', 1)[0]
                ),
                checkbox
            )
            for checkbox in checkbox_elements
        ])

        # If categories contains `Any` - skip selection
        unique_items = set(items)
        formatted_items = set(
            [
                self.__format_item(category)
                for category in unique_items
            ]
        )
        if "any" in formatted_items:
            return

        # Select items and save not_found_items
        not_found_items = []
        for category in unique_items:
            try:
                formatted_category = self.__format_item(category)
                self.browser_lib.click_element(
                    checkbox_by_value[formatted_category])
            except:
                not_found_items.append(category)

        if len(not_found_items) > 0:
            logger.warning(f"Unknown {filter}: {not_found_items}")

        # Verify selected items
        self.__verify_selected_items(
            not_found_items, formatted_items, filter_type)

    def sort_by_newest(self):
        logger.info("Sort by newest")
        # Define selectors
        sort_by_selector = 'css:[data-testid="SearchForm-sortBy"]'

        # Select
        value_to_select = 'newest'
        self.browser_lib.select_from_list_by_value(
            sort_by_selector, value_to_select)

        # Verify
        sort_by_element_value = self.browser_lib.get_selected_list_value(
            sort_by_selector)
        assert sort_by_element_value == value_to_select

    def expand_and_get_all_articles(self):
        logger.info("Expand all articles")
        # Define selectors
        show_more_button_selector = 'css:[data-testid="search-show-more-button"]'
        search_results_selector = 'css:[data-testid="search-results"]'
        search_result_selector = 'css:[data-testid="search-bodega-result"]'
        search_result_link_selector = 'css:[data-testid="search-bodega-result"] a'

        # Expand all elements
        self.__expand_all_elements(
            show_more_button_selector, search_results_selector
        )

        # Get all elements
        search_result_list = self.browser_lib.find_element(
            search_results_selector)
        search_result_items = self.browser_lib.find_elements(
            search_result_selector, search_result_list
        )
        logger.info("All articles count: " + str(len(search_result_items)))

        # Get unique elements
        unique_elements = self.__get_unique_elements(
            search_result_items, search_result_link_selector)
        logger.info("Unique articles count: " + str(len(unique_elements)))
        return unique_elements

    def parse_articles_data(self, articles, search_phrase):
        logger.info("Parse articles data")
        data = []
        for article in articles:
            try:
                # Parse article data
                article = self.parse_article_data(
                    article[0], search_phrase
                )
                data.append(article)
            except Exception as e:
                print(f"Failed to parse article data: {article[1]}", e)
        return data

    def parse_article_data(self, article_element, search_phrase):
        # Define selectors
        date_selector = 'css:[data-testid="todays-date"]'
        title_selector = 'css:a > h4'
        description_selector = 'css:a p:nth-child(2)'
        image_selector = 'css:img'

        # Get data
        date_element = self.browser_lib.find_element(
            date_selector, article_element)
        date = self.browser_lib.get_text(date_element)
        title_element = self.browser_lib.find_element(
            title_selector, article_element)
        title = self.browser_lib.get_text(title_element)
        try:
            description_element = self.browser_lib.find_element(
                description_selector, article_element)
            description = self.browser_lib.get_text(description_element)
        except:
            description = None
            logger.warning(f'No description found for: {title}')
        try:
            image_element = self.browser_lib.find_element(
                image_selector, article_element)
            image_url = self.__get_clean_url(
                self.browser_lib.get_element_attribute(image_element, 'src')
            )
        except:
            image_url = None

        return Article(search_phrase, title, date, description, image_url)

    # Helper Methods

    def __format_item(self, item: str) -> str:
        return item.replace(" ", "").lower()

    def __verify_selected_items(self, not_found_items, formatted_items, type):
        # Define selectors
        selected_item_container_selector = f'css:div.query-facet-{type}s'
        selected_item_selector = f'css:button[facet-name="{type}s"]'

        # Find container
        selected_items_container_element = self.browser_lib.find_element(
            selected_item_container_selector)

        # Find elements
        selected_item_elements = self.browser_lib.find_elements(
            selected_item_selector, selected_items_container_element)

        # Get element values
        selected_items_labels = [
            self.__format_item(self.browser_lib.get_element_attribute(
                category, 'value').split('|nyt:', 1)[0])
            for category in selected_item_elements
        ]
        not_found_items_formatted = [
            self.__format_item(item) for item in not_found_items]
        expected_selected_items = [
            item for item in formatted_items if item not in not_found_items_formatted]

        # Verify
        assert len(set(expected_selected_items).intersection(selected_items_labels)) == len(
            expected_selected_items), f"Selected {type} items don't match"

    def __parse_and_verify_date_range_from_ui(self, start_date_input_string, end_date_input_string) -> bool:
        # Define selectors
        date_range_selector = 'css:div.query-facet-date button[facet-name="date"]'
        # Get date range from UI element
        date_range_value = self.browser_lib.get_element_attribute(
            date_range_selector, 'value'
        )
        # Parse start and end dates
        parsed_start_date = re.search(
            "^\d{2}/\d{2}/\d{4}", date_range_value).group()
        parsed_end_date = re.search(
            "\d{2}/\d{2}/\d{4}$", date_range_value).group()
        # Validate
        matched = start_date_input_string == parsed_start_date and end_date_input_string == parsed_end_date
        return matched

    def __expand_all_elements(self, show_more_button_selector, search_results_selector):
        # Expand all elements
        while self.browser_lib.is_element_enabled(show_more_button_selector):
            try:
                self.browser_lib.scroll_element_into_view(
                    show_more_button_selector)
                self.browser_lib.click_element(show_more_button_selector)

            except Exception as e:
                logger.info("No more Show Button")
                break

        self.browser_lib.wait_until_element_is_enabled(
            search_results_selector, timeout=10
        )

    def __get_unique_elements(self, search_result_items, search_result_link_selector):
        # Make tuple with URLs
        tuple_items = [
            (
                element,
                self.__get_clean_url(
                    self.browser_lib.get_element_attribute(
                        self.browser_lib.find_element(
                            search_result_link_selector, element),
                        'href'
                    )
                )
            )
            for element in search_result_items
        ]

        # Filter by unique URL
        first_item = tuple_items.pop(0)
        unique_tuple_items = [first_item]
        seen_urls = {first_item[1]}
        for item in tuple_items:
            if item[1] not in seen_urls:
                unique_tuple_items.append(item)
                seen_urls.add(item[1])
        return unique_tuple_items

    def __get_clean_url(self, url) -> str:
        clean_url = urlunparse(list(urlparse(url)[:3]) + ['', '', ''])
        return clean_url
