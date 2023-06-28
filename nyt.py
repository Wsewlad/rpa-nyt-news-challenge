import concurrent.futures
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files
from home_page import HomePage
from search_page import SearchPage
from logger import logger


class NYT:
    def __init__(self):
        self.browser_lib = None
        self.home_page = None
        self.search_page = None

    def setup(self):
        logger.info('Setup')
        self.browser_lib = Selenium()
        self.browser_lib.auto_close = False
        self.browser_lib.set_selenium_implicit_wait(timedelta(seconds=15))

    @staticmethod
    def get_work_item_variables():
        logger.info('Get work item variables')
        library = WorkItems()
        library.get_input_work_item()
        return library.get_work_item_variables()

    def enter_search_query(self, search_phrase):
        self.home_page = HomePage(self.browser_lib)
        self.home_page.lend_first_page()
        self.home_page.enter_search_query(search_phrase)

    def set_search_filters(self, categories, sections, start_date, end_date):
        self.search_page = SearchPage(self.browser_lib)
        self.search_page.set_filters(categories, 'type')
        self.search_page.set_filters(sections, 'section')
        self.search_page.set_date_range(start_date, end_date)
        self.search_page.sort_by_newest()

    def parse_articles(self, search_phrase):
        article_elements = self.search_page.expand_and_get_all_articles()
        articles = self.search_page.parse_articles_data(
            article_elements, search_phrase
        )
        return articles

    @staticmethod
    def export_articles_to_excel_file(articles):
        logger.info('Export articles to excel file')
        excel_lib = Files()
        excel_lib.create_workbook(
            path=os.path.join('output', 'articles.xlsx'), fmt="xlsx", sheet_name="NYT")
        data = []
        for article in articles:
            row = article.make_excel_row()
            data.append(row)
        excel_lib.append_rows_to_worksheet(data, header=True)
        excel_lib.save_workbook()

    @staticmethod
    def download_pictures(articles):
        logger.info('Download pictures')
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(article.download_picture)
                       for article in articles]
            concurrent.futures.wait(futures)

    def execute(self):
        try:
            self.setup()
            variables = self.get_work_item_variables()
            search_phrase = variables["search_phrase"]
            categories = [var.replace(" ", "").lower()
                          for var in set(variables.get("categories", []))]
            sections = [var.replace(" ", "").lower()
                        for var in set(variables.get("sections", []))]
            number_of_month = variables.get("number_of_month", 0)
            number_of_month = number_of_month if number_of_month > 0 else 1
            end_date = datetime.now()
            start_date = end_date - relativedelta(months=number_of_month)

            self.enter_search_query(search_phrase)
            self.set_search_filters(categories, sections, start_date, end_date)
            articles = self.parse_articles(search_phrase)
            if len(articles) > 0:
                self.export_articles_to_excel_file(articles)
                self.download_pictures(articles)
            else:
                logger.warning("No articles")
            logger.info("Complete")

        except Exception as e:
            logger.exception(e, stack_info=True)
        finally:
            if self.browser_lib:
                logger.info("Capture page screenshot")
                self.browser_lib.capture_page_screenshot(
                    filename='output/end.png')
                self.browser_lib.close_all_browsers()
