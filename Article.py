import os
import re
from urllib.parse import urlparse
from RPA.HTTP import HTTP
from logger import logger


class Article:

    def __init__(self, search_phrase, title, date, description, image_url):
        self.search_phrase = search_phrase
        self.title = title
        self.date = date
        self.description = description
        self.image_url = image_url

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
