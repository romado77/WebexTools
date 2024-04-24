import argparse
import os

from webextools.disable_users import disable_users_main
from webextools.recordings_report import recording_report_main


def main():
    parser = argparse.ArgumentParser(description="WebexTools - Command-line tools for Cisco Webex")
    subparsers = parser.add_subparsers(title="Available Tools", dest="subparser_name", required=True)

    disable_users_parser = subparsers.add_parser(
        "disable-users", help="Disable Webex users based on CSV file"
    )

    disable_users_parser.add_argument("--file", "-f", help="CSV file with users data", required=True)
    disable_users_parser.add_argument(
        "--column", "-c", help="Column name to use for user email", default="email"
    )
    disable_users_parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Write the report to the file",
    )

    disable_users_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbose output (can be specified multiple times)",
    )

    disable_users_parser.add_argument("--dry-run", "-d", action="store_true", help="Dry run mode")
    disable_users_parser.set_defaults(func=disable_users_main)

    recording_report_parser = subparsers.add_parser(
        "recording-report", help="Generate recording audit report"
    )

    recording_report_parser.add_argument(
        "--period",
        "-p",
        type=int,
        default=90,
        help="Recording report period in days (default 90 days, max 365 days)",
    )
    recording_report_parser.add_argument(
        "--write",
        "-w",
        type=str,
        metavar="FILENAME",
        help="Specify the file name to write the report",
    )

    recording_report_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbose output (can be specified multiple times)",
    )
    recording_report_parser.set_defaults(func=recording_report_main)

    args = parser.parse_args()

    if args.verbose == 1:
        os.environ["VERBOSE"] = "1"

    if args.verbose > 1:
        os.environ["VERBOSE"] = "1"
        os.environ["DEBUG"] = "1"

    args.func(args)


if __name__ == "__main__":
    main()
