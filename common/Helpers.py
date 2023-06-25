# importt RPA modules
from RPA.HTTP import HTTP
# import system modules
import re
import os
from urllib.parse import urlparse

from common.Decorators import step_logger_decorator


def contains_money(title, description) -> bool:
    """
    Check if the given title or description contains any mention of money.

    Args:
        `title (str)`: The title text to be checked.
        `description (str)`: The description text to be checked.

    Returns:
       `bool`: True if the text contains a mention of money, False otherwise.

    Example:
    ```
        title = "New Product Launch: $19.99 Discount!"
        description = "Limited-time offer: Save $10 on your purchase"
        has_money = contains_money(title, description)
        print(has_money)  # Output: True
    ```
    """
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
    """
    Extract the file name from a given URL.

    Args:
        `url (str)`: The URL from which to extract the file name.

    Returns:
        `str`: The file name extracted from the URL.

    Example:
    ```
        url = "https://example.com/images/photo.jpg"
        file_name = get_file_name_from_url(url)
        print(file_name)  # Output: "photo.jpg"
    ```
    """
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    return file_name


def download_picture(url: str, path: str):
    """
    Download a picture from a given URL and save it to the specified path.

    Args:
        `url (str)`: The URL of the picture to download.\n
        `path (str)`: The path where the downloaded picture should be saved.

    Returns:
        `None`

    Example:
    ```
        url = "https://example.com/images/photo.jpg"
        path = "/path/to/save"
        download_picture(url, path)
    ```
    """
    http = HTTP()
    http.download(
        url=url,
        target_file=os.path.join(path, get_file_name_from_url(url)),
        overwrite=True
    )


def count_query_occurrences(query, title, description) -> int:
    """
    Count the occurrences of a query within the given title and description.

    Args:
        `query (str)`: The query to search for.\n
        `title (str)`: The title text to search within.\n
        `description (str | None)`: The description text to search within.

    Returns:
        `int`: The number of occurrences of the query within the title and description.

    Example:
    ```
        query = "apple"
        title = "Delicious Apple Pie Recipe"
        description = "This recipe teaches you how to make a classic apple pie."
        count = count_query_occurrences(query, title, description)
        print(count)  # Output: 2
    ```
    """
    text = title
    if description:
        text += ' ' + description
    return text.count(query)
