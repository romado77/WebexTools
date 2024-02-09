""" This is module to disable Webex Teams users from the CSV file."""
import argparse
import json
import os
import sys
from datetime import datetime

from webexteamssdk import ApiError, Person, WebexTeamsAPI

from webextools.helper import get_token, read_csv, verbose


def disable_users(api: WebexTeamsAPI, people: list[Person]) -> list[dict]:
    """
    Disable the users in the Webex Teams.

    :param api: WebexTeamsAPI object
    :param people: list of Person objects

    :return: list of user status
    """
    users = []

    for person in people:
        p = json.loads(person.to_json())
        p.update({"loginEnable": False, "callingData": False, "personId": person.id})

        status = {
            "personId": person.id,
            "displayName": person.displayName,
            "email": person.emails[0],
            "status": "Disabled",
        }

        try:
            api.people.update(**p)
            verbose(
                f"\033[92m[Success]\033[0m Disabling user: {person.displayName} ({person.emails[0]})"
            )
            status["update"] = "Success"
        except ApiError:
            verbose(
                f"\033[91m[Failed]\033[0m Unable to disable user: {person.displayName} ({person.emails[0]})"
            )
            status["update"] = "Failed"
        except Exception as e:
            print("Internal error occurred. Error: ", e)
            status["update"] = "Failed"

        users.append(status)

    return users


def get_people(api: WebexTeamsAPI, emails: list[str]) -> list[Person]:
    """
    Get the people from the Webex Teams API.

    :param api: WebexTeamsAPI object
    :param emails: list of user emails

    :return: list of Person objects
    """
    try:
        users = api.people.list()
        return [user for user in users if user.emails[0] in emails]
    except ApiError as e:
        print("Error occurred while fetching user data. Error: ", e)
    except Exception as e:
        print("Internal error occurred. Error: ", e)

    sys.exit(1)


def get_emails_from_csv(args: argparse.Namespace) -> list[str]:
    """
    Get the user emails from the CSV file.

    :param args: argparse.Namespace object
    :return: list of user emails
    """
    users = read_csv(args.file, args.column)
    emails = [user["email"] for user in users if user.get("email", "")]

    if not emails:
        print("No users found in the CSV file.")
        exit(1)

    return emails


def disable_users_main(args: argparse.Namespace) -> None:
    """
    Main function to disable inactive Webex Teams users.

    :param args: argparse.Namespace object
    """
    token = get_token()

    api = WebexTeamsAPI(access_token=token)

    emails = get_emails_from_csv(args)
    people = get_people(api, emails)

    if not people:
        print("No users found in the Webex Teams.")
        exit(1)

    disabled_users = disable_users(api, people)

    if args.report:
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"disabled_users_report.{current_datetime}.json"

        with open(filename, "w") as f:
            json.dump(disabled_users, f, indent=4)

        print(f"\nReport written to {os.path.abspath(filename)}\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Disable Webex Teams users.")
    parser.add_argument("--file", "-f", help="CSV file with users data", required=True)
    parser.add_argument("--column", "-c", help="Column name to use for user email", default="email")
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Write the report to the file",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    if args.verbose:
        os.environ["VERBOSE"] = "1"

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    disable_users_main(args)
