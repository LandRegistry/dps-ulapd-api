import time
import datetime


# Converts filesizes in bytes into human readable units
def format_file_size(bytes):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    value = bytes
    while value > 1000 and i < len(units) - 1:
        value = float(value / 1000)
        i = i + 1
    return str(round(value, 2)) + ' ' + units[i]


# Converts "dd-mm-YYYY" to "MONTH YYYY"
def format_last_updated_date(string, pattern="%-d %B %Y"):
    date_timestamp = datetime.datetime.strptime(string, "%d-%m-%Y").timetuple()
    last_updated = time.strftime(pattern, date_timestamp)
    return last_updated
