import os
import re
from urllib.parse import urlparse
from RPA.HTTP import HTTP
from logger import logger


class Article:

    def __init__(self, browser_lib, article_element, search_phrase):
        # Define selectors.
        date_selector = 'css:[data-testid="todays-date"]'
        title_selector = 'css:a > h4'
        description_selector = 'css:a p:nth-child(2)'
        image_selector = 'css:img'

        # Get data.
        self.search_phrase = search_phrase
        date_element = browser_lib.find_element(
            date_selector, article_element)
        self.date = browser_lib.get_text(date_element)
        title_element = browser_lib.find_element(
            title_selector, article_element)
        self.title = browser_lib.get_text(title_element)
        try:
            description_element = browser_lib.find_element(
                description_selector, article_element)
            self.description = browser_lib.get_text(description_element)
        except Exception as e:
            self.description = None
            logger.warning(f'No description found for: {self.title} - {e}')
        try:
            image_element = browser_lib.find_element(
                image_selector, article_element)
            self.image_url = browser_lib.get_element_attribute(
                image_element, 'src')
        except Exception as e:
            logger.warning(f'No image found for: {self.title} - {e}')
            self.image_url = None

    def make_excel_row(self):
        row = {
            'Date': self.date,
            'Title': self.title,
            'Search Phrases Count': self.search_phrase_occurrences_count(),
            'Description': self.description or 'No description found',
            'Contains Money': self.contains_money(),
            'Picture Filename': self.get_file_name() or "No picture found"
        }
        return row

    def download_picture(self):
        if self.image_url:
            http = HTTP()
            file_path = os.path.join('output', 'images', self.get_file_name())
            http.download(
                url=self.image_url,
                target_file=file_path,
                overwrite=True
            )
        else:
            logger.warning(f'No picture found for: {self.title}')

    def get_file_name(self):
        parsed_url = urlparse(self.image_url)
        file_name = os.path.basename(parsed_url.path)
        return file_name

    def contains_money(self) -> bool:
        pattern = r'\$[\d,.]+|\d+\s?(dollars|USD)'
        text = self.title
        if self.description:
            text += ' ' + self.description
        matches = re.findall(pattern, text)
        if matches:
            return True
        else:
            return False

    def search_phrase_occurrences_count(self) -> int:
        text = self.title
        if self.description:
            text += ' ' + self.description
        return text.count(self.search_phrase)
