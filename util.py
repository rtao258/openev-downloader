import re
import requests
import sys
import datetime as dt


def get_or_stop(url):
    # TODO: use *args and **kwargs
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print(f"Error connecting to {url}!")
        print(f"1. Check that your device is connected to the internet.")
        print(f"2. Check that you can access the above link in a browser.")
        print(f"3. File a bug report on our GitHub page.")
        sys.exit(1)
    return r


def current_time():
    """
    Returns the current time formatted in a particular format.
    :return: the current time formatted as YYYY-MM-DD-HH-MM-SS
    """
    now = dt.datetime.now()
    year = str(now.year).zfill(4)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)
    hour = str(now.hour).zfill(2)
    minute = str(now.minute).zfill(2)
    second = str(now.second).zfill(2)
    return "-".join([year, month, day, hour, minute, second])


def clean_filename(unclean_name: str) -> str:
    """
    Return a valid filename where any character that is not
    a letter, number, dash, underscore, space, or period
    is replaced with an underscore
    """
    return re.sub(r'[^\w\-_. ]', '_', unclean_name)