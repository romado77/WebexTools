import csv
import os
from datetime import datetime, timedelta
from typing import Optional

WEBEX_BASE_URL = "https://webexapis.com/v1/"
RESOURCE_URIS = {
    "people": "people",
    "pmr": "meetingPreferences/personalMeetingRoom",
    "reports": "reports",
}


def verbose(message: str) -> None:
    """
    Log the message to the console if the VERBOSE environment variable is set.

    :param message: message to log
    """
    if os.getenv("VERBOSE") is not None:
        print(message)


def get_url(resource: str, *params):
    """
    Get URL for the specified resource.
    :param resource: resource name.
    :param params: request parameters.
    :return: URL.
    """
    uri = RESOURCE_URIS.get(resource)

    if uri is None:
        return

    if params:
        return WEBEX_BASE_URL + RESOURCE_URIS[resource] + "/" + "/".join(params)

    return WEBEX_BASE_URL + RESOURCE_URIS[resource]


def read_csv(filename: str, columns: Optional[list]) -> list:
    """
    Read CSV file and return the data as a list of dictionaries.

    :param filename: file name or filepath
    :param columns: list of columns to include in the result
    :return: list of dictionaries for each row in the CSV file
    """

    if isinstance(columns, str):
        columns = [columns]

    if not isinstance(columns, list):
        columns = []

    with open(filename, "r", encoding="utf-8-sig") as f:
        data = list(csv.DictReader(f))

    if not columns:
        return data

    return [
        {k.strip().lower(): v for k, v in row.items() if k.strip().lower() in columns}
        for row in data
    ]


def write_csv(data: list[dict], csv_filename) -> str:
    """
    Write data to a CSV file.

    :param data: list of dictionaries.
    :param csv_filename: CSV file name or filepath.

    :return: CSV file name or empty string if an error occurred.
    """
    keys = data[0].keys() if data else []

    if not csv_filename.endswith(".csv"):
        csv_filename += ".csv"

    try:
        with open(csv_filename, "w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=keys)

            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print("Error writing to CSV file:", e)
        return ""

    return csv_filename


def remove_file(filename: str) -> None:
    """
    Check if the result file exists, if so, remove it.

    :param filename: file name or filepath.
    """
    if os.path.exists(filename):
        os.remove(filename)


def file_exists(filename: str) -> bool:
    """
    Check if the result file exists, if so, remove it.
    :param filename: file name or filepath.
    """
    return os.path.isfile(filename)


def generate_time_ranges(total_days: int = 90, span: int = 7) -> list:
    """
    Generate time ranges for the specified number of days.

    :param total_days: total number of days.
    :param span: number of days for each range.
    :return: list of time ranges.
    """
    if total_days > 365 or span > 90:
        raise ValueError("Total days must be <= 365 and chunk days must be <= 90")

    current_time = datetime.now()
    time_ranges = []

    for i in range(0, total_days, span):
        if i + span > total_days:
            span = total_days - i
        start_date = (
            (current_time - timedelta(days=i + span, seconds=1))
            .replace(hour=23, minute=59, second=59)
            .strftime("%Y-%m-%dT%H:%M:%S")
        )
        end_date = (current_time - timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%S")
        time_ranges.append((start_date, end_date))

    return time_ranges


def get_token() -> str:
    """
    Get the Webex API access token.

    :return: Webex API access token
    """
    token = os.environ.get("WEBEX_TEAMS_ACCESS_TOKEN")

    if token is not None:
        return token

    token = input("\nEnter your Webex API access token: ")

    if not token.strip():
        print("Invalid token provided.")

        get_token()

    return token.strip()
