import csv
import getpass
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Optional

from webextools.settings import DEFAULT_BASE_URL, RESOURCE_URIS


def verbose(message: str) -> None:
    """
    Log the message to the console if the VERBOSE environment variable is set.

    :param message: message to log
    """
    if os.getenv("VERBOSE") is not None:
        print(message)


def debug(message: str) -> None:
    """
    Log the message to the console if the DEBUG environment variable is set.

    :param message: message to log
    """
    if os.getenv("DEBUG") is not None:
        print(message)


def error(message: str, exc: Optional[Exception] = None) -> None:
    """
    Log the error message to the console.

    :param message: error message
    :param exc: exception
    """
    print(f"\033[91m{message}\033[0m")

    if not isinstance(exc, Exception):
        return

    if hasattr(exc, "response"):
        status_code = exc.response.status_code
        reason_phrase = exc.response.reason_phrase

        text = json.loads(exc.response.text)

        message = text.get("message", "")
        tracking_id = text.get("trackingId", "")

        if message:
            err_message = f"\nError: {status_code} ({reason_phrase}) - {message}\n"
        else:
            err_message = f"\nError: {status_code} ({reason_phrase})\n"

        if os.getenv("DEBUG") is not None:
            err_message += f"Tracking ID: {tracking_id}"
    else:
        err_message = f"\nError: {str(exc)}\n"

    print(err_message, "\n")


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
        return DEFAULT_BASE_URL + "/" + RESOURCE_URIS[resource] + "/" + "/".join(params)

    return DEFAULT_BASE_URL + "/" + RESOURCE_URIS[resource]


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

    return [{k.strip(): v for k, v in row.items() if k.strip() in columns} for row in data]


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
        with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=keys)

            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        error("Error writing to CSV file:", e)
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


def generate_time_ranges(total_days: int = 0, span: int = 0) -> list:
    """
    Generate time ranges for the specified number of days.

    :param total_days: total number of days.
    :param span: number of days for each range.
    :return: list of time ranges.
    """
    if not total_days or not span:
        raise ValueError("Invalid value for total_days or span.")

    if total_days < span:
        span = total_days

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


def prompt_token() -> str:
    """
    Prompt the Webex API access token.

    :return: Webex API access token
    """
    token = os.environ.get("WEBEX_TEAMS_ACCESS_TOKEN")

    if token is not None:
        return token

    print()
    token = getpass.getpass(" Enter your Webex API access token: ")
    print()

    if not token.strip():
        print("Invalid token provided, token cannot be empty.")

        prompt_token()

    return token.strip()


def get_org_id_from_token(token: str) -> str:
    """
    Get the organization ID from the Webex API access token.

    :param token: Webex API access token
    :return: Organization ID

    :raises: ValueError if the token is invalid
    """
    if "_" not in token:
        print("Invalid Webex API access token.")
        sys.exit(1)

    parts = token.split("_")
    org_id = parts[-1]

    if not uuid.UUID(org_id):
        print("Invalid organization ID.")
        sys.exit(1)

    return org_id
