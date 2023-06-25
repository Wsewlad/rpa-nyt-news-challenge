# import system modules
import os
# import custom modules
import common.Helpers as helpers
from common.Dates import convert_string_to_date


class Article:

    def __init__(self, search_phrase, title, date, description, image_url):
        self.search_phrase = search_phrase
        self.title = title
        self.date = date
        self.description = description
        self.image_url = image_url

    def make_excel_row(self):
        """
        Creates a dictionary representing a row of data for an article to be written into an Excel file.

        Returns:
            `dict`: A dictionary representing the row of data for the article.

        Usage:
        ```
            article = Article(date='2023-05-30', title='Sample Article', search_phrase='example search', description='This is an example article.', image_url='https://example.com/image.jpg')
            row = article.make_excel_row()
            # {'Date': '2023-05-30', 'Title': 'Sample Article', 'Search Phrases Count': 1, 'Description': 'This is an example article.', 'Contains Money': False, 'Picture Filename': 'image.jpg'}
        ```
        """
        row = {
            'Date': convert_string_to_date(self.date).strftime("%Y-%m-%d %H:%M:%S"),
            'Title': self.title,
            'Search Phrases Count': helpers.count_query_occurrences(self.search_phrase, self.title, self.description),
            'Description': self.description or 'No description found',
            'Contains Money': helpers.contains_money(self.title, self.description),
            'Picture Filename': helpers.get_file_name_from_url(self.image_url) or "No picture found"
        }
        return row

    def download_picture(self):
        """
        Downloads the picture associated with the article.

        Usage:
        ```
            article = Article(date='2023-05-30', title='Sample Article', search_phrase='example search', description='This is an example article.', image_url='https://example.com/image.jpg')
            article.download_picture()
            # The picture from the URL 'https://example.com/image.jpg' is downloaded and saved to the 'output/images' directory.
        ```
        """
        if self.image_url:
            helpers.download_picture(
                self.image_url, os.path.join('output', 'images')
            )
        else:
            print(f'No picture found for: {self.title}')
