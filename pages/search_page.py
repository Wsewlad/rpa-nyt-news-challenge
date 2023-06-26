# import RPA modules
from RPA.Browser.Selenium import Selenium
# import system modules
from urllib.parse import urlparse, parse_qs, urlunparse
import re
# import custom modules
import constants as Const
from common.Decorators import exception_decorator, step_logger_decorator
from models.Article import Article


class SearchPage:

    def __init__(self, browser_lib: Selenium):
        self.browser_lib = browser_lib
        title = self.browser_lib.get_title()
        assert title == "The New York Times - Search", "This is not Search Page, current page is - " + \
            self.browser_lib.get_location()

    @exception_decorator("Set Date Range")
    @step_logger_decorator("Set Date Range")
    def set_date_range(self, start_date, end_date):
        """
        Set and verify the date range for the search.

        Args:
            `start_date (datetime.date)`: The start date of the date range.\n
            `end_date (datetime.date)`: The end date of the date range.
        """
        # Define selectors
        search_date_dropdown_selector = 'css:[data-testid="search-date-dropdown-a"]'
        specific_dates_selector = 'css:[value="Specific Dates"]'
        date_range_start_date_selector = 'css:[data-testid="DateRange-startDate"]'
        date_range_end_date_selector = 'css:[data-testid="DateRange-endDate"]'

        # Navigate to date range picker
        self.browser_lib.click_element(search_date_dropdown_selector)
        self.browser_lib.click_element(specific_dates_selector)

        # Get date strings in appropriate format
        start_date_input_string = start_date.strftime(Const.DATE_INPUT_FORMAT)
        end_date_input_string = end_date.strftime(Const.DATE_INPUT_FORMAT)
        start_date_query_string = start_date.strftime(Const.DATE_QUERY_FORMAT)
        end_date_query_string = end_date.strftime(Const.DATE_QUERY_FORMAT)

        # Input dates
        self.browser_lib.input_text(
            date_range_start_date_selector, start_date_input_string
        )
        self.browser_lib.input_text(
            date_range_end_date_selector, end_date_input_string)
        self.browser_lib.press_keys(date_range_end_date_selector, "ENTER")

        # Validate selected dates
        self.__verify_date_entries(
            start_date_input_string, end_date_input_string, start_date_query_string, end_date_query_string)

    @exception_decorator("Set Filters")
    @step_logger_decorator("Set Filters")
    def set_filters(self, items, filter_type):
        """
        Set the filters for the search.

        This method selects the specified filter items based on the filter type.

        Args:
            `items (list[str])`: A list of filter items to select.\n
            `filter_type (str)`: The type of filter to apply. Valid values are 'type' and 'section'.

        Raises:
            `Exception`: If the filter_type is not 'type' or 'section'.

        Example:
        ```
            browser_lib = Selenium()
            search_page = SearchPage(browser_lib)
            sections = ['Opinion', 'Politics']
            filter_type = 'section'
            nytimes.set_filters(sections, filter_type)
        ```
        """
        if filter_type not in ['type', 'section']:
            raise Exception(f"Undefined filter type: {filter_type}")

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
        print("Unknown filters: ", not_found_items)

        # Verify selected items
        self.__verify_selected_items(
            not_found_items, formatted_items, filter_type)

    @exception_decorator("Sort By Newest")
    @step_logger_decorator("Sort By Newest")
    def sort_by_newest(self):
        """
        Sort the search results by newest.

        This method selects the 'newest' option from the sort by dropdown menu.
        """
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

    @exception_decorator("Expand And Get All Articles")
    @step_logger_decorator("Expand And Get All Articles")
    def expand_and_get_all_articles(self):
        """
         Expand all articles in the search results and retrieve the unique articles.

         This method expands all articles by clicking the 'Show More' button until all articles are displayed.
         It then retrieves all the articles and filters out duplicate articles to return only the unique ones.

         Returns:
             `list[tuple[any, str]]`: A list of tuples representing unique articles.\n
             Each tuple contains an element and its corresponding URL.
         """
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
        print("All articles count: " + str(len(search_result_items)))

        # Get unique elements
        unique_elements = self.__get_unique_elements(
            search_result_items, search_result_link_selector)
        print("Unique articles count: " + str(len(unique_elements)))
        return unique_elements

    @step_logger_decorator("Parse Articles Data")
    @exception_decorator("Parse Articles Data")
    def parse_articles_data(self, articles, search_phrase):
        """
        Parse the data of multiple articles.

        Args:
            `articles (list)`: A list of article elements.\n
            `search_phrase (str)`: The search phrase used to retrieve the articles.

        Returns:
            `list`: A list of Article objects containing the parsed data of the articles.
        """
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

    @exception_decorator("Parse Article Data")
    def parse_article_data(self, article_element, search_phrase):
        """
        Parse the data of an article element.

        Args:
            `article_element`: The element representing the article.\n
            `search_phrase (str)`: The search phrase used to retrieve the articles.

        Returns:
            `Article`: An instance of the Article class containing the parsed data.
        """
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
            print(f'No description found for: {title}')
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
        """
        Verify the selected items on UI against the expected filter items of a specific type.

        Args:
            `not_found_items (list)`: A list of items that were not found.\n
            `formatted_items (set)`: A set of formatted items representing the expected items.\n
            `type (str)`: The type of the items to verify ('type' or 'section').

        Raises:
            `AssertionError`: If the selected items do not match the expected items.
        """
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

    def __verify_date_entries(self, start_date_input_string, end_date_input_string, start_date_query_string, end_date_query_string):
        """
        Parse and validate dates from the current URL query parameters and perform additional validation with page reload.

        This method retrieves the current URL query parameters, parses and validates the start and end dates from the query parameters. It also performs date range validation from the UI. If the date range from the UI does not match the expected range, the page is reloaded and the validation is performed again.

        Args:
            start_date_input_string (str): The input string representing the start date.
            end_date_input_string (str): The input string representing the end date.
            start_date_query_string (str): The expected start date in the query parameters.
            end_date_query_string (str): The expected end date in the query parameters.

        Raises:
            AssertionError: If the start date or end date from the query parameters do not match the expected values, or if the date range from the UI does not match the expected range.
        """
        # Parse dates from current url query params
        current_url = urlparse(self.browser_lib.get_location())
        query_params = parse_qs(current_url.query)
        parsed_start_date_query = query_params.get('startDate', [''])[0]
        parsed_end_date_query = query_params.get('endDate', [''])[0]

        # Validate date range from query params
        assert parsed_start_date_query == start_date_query_string, "Start date doesn't match"
        assert parsed_end_date_query == end_date_query_string, "End date doesn't match"

        # Validate date range from UI
        matched = self.__parse_and_verify_date_range_from_ui(
            start_date_input_string, end_date_input_string)
        if not matched:
            self.browser_lib.reload_page()
        matched = self.__parse_and_verify_date_range_from_ui(
            start_date_input_string, end_date_input_string)
        assert matched, "Date range from UI doesn't match"

    def __parse_and_verify_date_range_from_ui(self, start_date_input_string, end_date_input_string) -> bool:
        """
        Parse and verify the date range from the UI element.

        This method retrieves the date range value from the UI element and parses it to extract the start and end dates. It then compares the parsed dates with the input date strings to validate the date range.

        Args:
            `start_date_input_string (str)`: The input string representing the start date.\n
            `end_date_input_string (str)`: The input string representing the end date.

        Returns:
            `bool`: True if the parsed start and end dates from the UI match the input date strings, False otherwise.
        """
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
        """
        Expand all elements by clicking the 'Show More' button until it is no longer visible.

        Args:
            `show_more_button_selector (str)`: The CSS selector for the 'Show More' button.\n
            `search_results_selector (str)`: The CSS selector for the search results container.
        """

        # Expand all elements
        while self.browser_lib.is_element_enabled(show_more_button_selector):
            try:
                self.browser_lib.scroll_element_into_view(
                    show_more_button_selector)
                self.browser_lib.click_element(show_more_button_selector)

            except Exception as e:
                print("No more Show Button -", str(e))
                break

        self.browser_lib.wait_until_element_is_enabled(
            search_results_selector, timeout=10
        )

    def __get_unique_elements(self, search_result_items, search_result_link_selector):
        """
        Extract unique URL subelements from search result items.

        This method extracts the URL subelements from the search result items, removes query parameters from the URLs, and filters the elements to get only unique elements based on their URLs.

        Args:
            `search_result_items (list)`: A list of search result items.\n
            `search_result_link_selector (str)`: The CSS selector for the search result link elements.

        Returns:
            `list`: A list of tuples containing unique search result items and their corresponding cleaned URLs.
        """
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
        """
        Get a clean version of the URL without query parameters or fragments.

        This method takes a URL and removes any query parameters or fragments, returning a clean version of the URL.

        Args:
            `url (str)`: The input URL.

        Returns:
            `str`: The clean URL without query parameters or fragments.

        """
        clean_url = urlunparse(list(urlparse(url)[:3]) + ['', '', ''])
        return clean_url
