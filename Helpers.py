from RPA.HTTP import HTTP
import re
import os
from urllib.parse import urlparse

from Decorators import step_logger_decorator


def contains_money(title, description) -> bool:
    pattern = r'\$[\d,.]+|\d+\s?(dollars|USD)'
    text = title
    if description:
        text += ' ' + description
    matches = re.findall(pattern, text)
    if matches:
        return True
    else:
        return False


def get_file_name_from_url(url):
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    return file_name


def download_picture(url: str, path: str):
    http = HTTP()
    http.download(
        url=url,
        target_file=os.path.join(path, get_file_name_from_url(url)),
        overwrite=True
    )


def count_query_occurrences(query, title, description) -> int:
    text = title
    if description:
        text += ' ' + description
    return text.count(query)
