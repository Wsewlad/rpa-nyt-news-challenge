import os
import Helpers as helpers


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
            'Search Phrases Count': helpers.count_query_occurrences(self.search_phrase, self.title, self.description),
            'Description': self.description or 'No description found',
            'Contains Money': helpers.contains_money(self.title, self.description),
            'Picture Filename': helpers.get_file_name_from_url(self.image_url) or "No picture found"
        }
        return row

    def download_picture(self):
        if self.image_url:
            helpers.download_picture(
                self.image_url, os.path.join('output', 'images')
            )
        else:
            print(f'No picture found for: {self.title}')
