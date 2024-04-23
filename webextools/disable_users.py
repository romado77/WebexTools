"""This is module to disable Webex Teams users from the CSV file."""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime

from webextools.helper import get_org_id_from_token, get_token, read_csv, verbose
from webextools.scim import SCIM
from webextools.users import User

terminal_width = shutil.get_terminal_size().columns


def disable_users(api: SCIM, users: list[User]) -> list[dict]:
    """
    Disable the users in the Webex Teams.

    :param api: SCIM API object
    :param people: list of Person objects

    :return: list of user status
    """
    report = []

    for user in users:
        status = {"id": user.id, "email": user.user_name, "updated": ""}

        if not user.active:
            verbose(
                f"\033[93m[Skipped]\033[0m User is already disabled: {user.display_name} ({user.user_name})"
            )
            status["updated"] = "Skipped"
            report.append(status)
            continue

        try:
            response = api.update_user_patch(
                user.id,
                {
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                    "Operations": [{"op": "replace", "value": {"active": False}}],
                },
            )
            if not isinstance(response, User) or response.active:
                verbose(
                    f"\033[91m[Failed]\033[0m Unable to disable user: {user.display_name} ({user.user_name})"
                )
                status["updated"] = "Failed"
            else:
                verbose(
                    f"\033[92m[Success]\033[0m Disabling user: {user.display_name} ({user.user_name})"
                )
                status["updated"] = "Success"
            report.append(status)
        except Exception as e:
            print("Internal error occurred. Error: ", e)
            verbose(
                f"\033[91m[Failed]\033[0m Unable to disable user: {user.display_name} ({user.user_name})"
            )
            verbose(f"Error: {e}")
            status["updated"] = "Failed"
            report.append(status)

    return report


def get_users(api: SCIM, emails: list[str]) -> list[User]:
    """
    Get the users from the Webex SCIM API.

    :param api: SCIM API object
    :param emails: list of user emails

    :return: list of User objects
    """
    try:
        return [user for user in api.get_users() if user.user_name in emails]
    except Exception as e:
        print("Internal error occurred. Error: ", e)

    sys.exit(1)


def get_emails_from_csv(args: argparse.Namespace) -> list[str]:
    """
    Get the user emails from the CSV file.

    :param args: argparse.Namespace object
    :return: list of user emails
    """
    emails = []

    email = args.column
    users = read_csv(args.file, email)

    for user in users:
        if not user.get(email, ""):
            continue

        if "@" not in user[email]:
            verbose(f"Invalid email address: {user[email]}")
            continue

        emails.append(user[email])

    if not emails:
        print(f"No users found in the column '{email}' of the CSV file.")
        exit(1)

    return emails


def disable_users_main(args: argparse.Namespace) -> None:
    """
    Main function to disable inactive Webex Teams users.

    :param args: argparse.Namespace object
    """
    token = get_token()
    org_id = get_org_id_from_token(token)

    api = SCIM(token=token, org_id=org_id)

    emails = get_emails_from_csv(args)
    users = get_users(api, emails)

    if not users:
        print("No users found in the Webex Teams.")
        exit(1)

    if args.dry_run:
        dry_run(users)

    disabled_users = disable_users(api, users)

    if args.report:
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"disabled_users_report.{current_datetime}.json"

        with open(filename, "w") as f:
            json.dump(disabled_users, f, indent=4)

        print(f"\nReport written to {os.path.abspath(filename)}\n")


def dry_run(users: list[User]) -> None:
    """
    Dry run to print the users data.

    :param users: list of User objects
    """
    print("\033[91m\nDry run mode is enabled, no users will be deleted!\n\033[0m")

    if terminal_width > 123:
        data = [
            {
                "name": user.display_name,
                "email": user.user_name,
                "id": user.id,
                "active": "\033[92m\u2713\033[0m" if user.active else "\033[91m\u2717\033[0m",
            }
            for user in users
        ]

        print("-" * 124)
        print("| {:^30} | {:^30} | {:^40} | {:^12}|".format("Username", "Email", "ID", "Active"))
        print("-" * 124)

        for row in data:
            print(
                f"| {row['name']: <30} | {row['email']: <30} | {row['id']: ^40} | {row['active']: ^20} |"
            )
            print("-" * 124)
    else:
        data = [
            {
                "name": user.display_name
                if len(user.display_name) < 28
                else user.display_name[:25] + "...",
                "email": user.user_name if len(user.user_name) < 28 else user.user_name[:25] + "...",
                "active": "\033[92m\u2713\033[0m" if user.active else "\033[91m\u2717\033[0m",
            }
            for user in users
        ]

        print("-" * 78)
        print("| {:^28} | {:^28} | {:^12} |".format("Username", "Email", "Active"))
        print("-" * 78)

        for row in data:
            print(f"| {row['name']: <28} | {row['email']: <28} | {row['active']: ^22} |")
            print("-" * 78)

    exit(0)


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
