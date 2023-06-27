from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
import concurrent.futures
from excel import export_articles_to_excel_file
from Dates import get_date_range
from Decorators import step_logger_decorator
from HomePage import HomePage
from SearchPage import SearchPage


class NYT:
    def __init__(self):
        self.browser_lib = None
        self.home_page = None
        self.search_page = None

    def setup(self):
        # Init browser lib
        self.browser_lib = Selenium()
        self.browser_lib.auto_close = False
        self.browser_lib.set_selenium_implicit_wait(15)

    def get_work_item_variables(self):
        library = WorkItems()
        library.get_input_work_item()
        return library.get_work_item_variables()

    def enter_search_query(self, search_phrase):
        # Home page logic
        self.home_page = HomePage(self.browser_lib)
        self.home_page.lend_first_page()
        self.home_page.enter_search_query(search_phrase)

    def set_search_filters(self, categories, sections, start_date, end_date):
        # Search page logic
        self.search_page = SearchPage(self.browser_lib)
        # Set filters
        if len(categories) > 0:
            self.search_page.set_filters(categories, 'type')
        else:
            print("No category filters provided")
        if len(sections) > 0:
            self.search_page.set_filters(sections, 'section')
        else:
            print("No section filters provided")
        self.search_page.set_date_range(start_date, end_date)
        self.search_page.sort_by_newest()

    def parse_articles(self, search_phrase):
        # Get all unique article elements
        articleElements = self.search_page.expand_and_get_all_articles()
        # Parse article's data
        articles = self.search_page.parse_articles_data(
            articleElements, search_phrase
        )
        return articles

    @step_logger_decorator("Download Pictures")
    def download_pictures(self, articles):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit download_image function for each article
            futures = [executor.submit(article.download_picture)
                       for article in articles]
            # Wait for all tasks to complete
            concurrent.futures.wait(futures)

    def execute(self):
        try:
            self.setup()
            variables = self.get_work_item_variables()
            try:
                search_phrase = variables["search_phrase"]
            except:
                raise Exception("No search_phrase variable provided")
            categories = variables.get("categories", [])
            sections = variables.get("sections", [])
            number_of_month = variables.get("number_of_month", 0)
            start_date, end_date = get_date_range(number_of_month)

            self.enter_search_query(search_phrase)
            self.set_search_filters(categories, sections, start_date, end_date)
            articles = self.parse_articles(search_phrase)
            if len(articles) == 0:
                print("No articles")
                return
            export_articles_to_excel_file(articles)
            self.download_pictures(articles)

        except Exception as e:
            print("An error occurred:", str(e))
            if self.browser_lib:
                self.browser_lib.capture_page_screenshot(
                    filename='output/error.png')
        finally:
            print("End")
            if self.browser_lib:
                self.browser_lib.capture_page_screenshot(
                    filename='output/end.png')
                self.browser_lib.close_all_browsers()
