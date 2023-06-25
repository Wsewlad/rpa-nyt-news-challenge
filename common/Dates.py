import datetime


def get_date_range(months):
    """
    Calculate the date range based on the number of past months.

    Args:
        `months (int)`: Number of past months to include in the date range.

    Returns:
        `tuple`: A tuple containing the start date and end date of the date range.

    Example:
    ```
        start_date, end_date = get_date_range(3)
        print(start_date)  # Output: 2023-03-01
        print(end_date)  # Output: 2023-05-30
    ```
    """
    current_date = datetime.date.today()
    current_year = current_date.year
    current_month = current_date.month

    start_date = datetime.date(current_year, current_month, 1)
    end_date = current_date

    if months > 0:
        for i in range(1, months):
            prev_month = current_month - i
            if prev_month <= 0:
                prev_month += 12
                current_year -= 1
            start_date = datetime.date(current_year, prev_month, 1)

    return start_date, end_date


def get_time_tuple(current_time):
    """
    Takes a time value in seconds and returns a tuple containing the equivalent minutes, seconds, and milliseconds.

    Args:
        `current_time (float)`: The time value in seconds.
    Returns:
        `tuple`: A tuple containing the `minutes, seconds, and milliseconds` extracted from the current_time value.
    """
    minutes = int(current_time // 60)
    seconds = int(current_time % 60)
    milliseconds = int((current_time % 1) * 1000)
    return minutes, seconds, milliseconds


def convert_string_to_date(date_string):
    current_date = datetime.datetime.now()

    if 'ago' in date_string:
        # Handle "Xh ago" format
        hours_ago = int(date_string.split('h')[0])
        date = current_date - datetime.timedelta(hours=hours_ago)
    else:
        # Handle "Month day" format
        date = datetime.datetime.strptime(date_string, "%B %d").date()
        date = date.replace(year=current_date.year)

    return date
