""" This is module to generate a report of Webex Teams users who requested recording data. """
import argparse
import json
import os
import sys

from webexteamssdk import ApiError, WebexTeamsAPI

from webextools.helper import generate_time_ranges, get_token, write_csv


def get_recording_report(api: WebexTeamsAPI, _from: str, to: str):
    """
    Get the recording report for a person.

    :param api: The Webex Teams API object.
    :param _from: The date to get the report from.
    :param to: The date to get the report to.
    """

    try:
        response = api.recording_report.access_summary(hostEmail="all", _from=_from, to=to)

        return [res.to_dict() for res in response]
    except ApiError as e:
        print(e)
        sys.exit(1)


def get_detailed_report(api: WebexTeamsAPI, recording_id: str) -> dict:
    """
    Get the detailed report for a person.

    :param api: The Webex Teams API object.
    :param recording_id: The recording id to get the detailed report for.
    """

    try:
        response = api.recording_report.access_detail(recording_id)
        return response.to_dict()

    except ApiError as e:
        print(e)
        sys.exit(1)


def parse_arguments():
    """
    Parse the command line arguments.

    :return: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Recording audit report")
    parser.add_argument(
        "--period",
        "-p",
        type=int,
        default=90,
        help="Recording report period in days (default 90 days, max 365 days)",
    )
    parser.add_argument(
        "--span",
        "-s",
        type=int,
        default=7,
        help="Recording report span in days (default 7 days, max 90 days)",
    )
    parser.add_argument(
        "--write",
        "-w",
        type=str,
        metavar="FILENAME",
        help="Specify the file name to write the report",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed information",
    )

    return parser.parse_args()


def prepare_detailed_report_from_summary(api: WebexTeamsAPI, recording: dict):
    """
    Prepare the detailed report for specific recording.

    :param api: The Webex Teams API object.
    :param recording: The recording to prepare the detailed report for
    :return: The prepared detailed report
    """
    report = []
    recording_id = recording["recordingId"]

    result = get_detailed_report(api, recording_id).get("items", [])

    if not result:
        return []

    for i in result:
        report.append(
            {
                "recordingId": recording["recordingId"],
                "topic": recording["topic"],
                "timeRecorded": recording["timeRecorded"],
                "requestorName": i.get("name", ""),
                "requestorEmail": i.get("email", ""),
                "accessTime": i["accessTime"],
                "downloaded": i["downloaded"],
                "viewed": i["viewed"],
            }
        )

    return report


def prepare_summary_report(api: WebexTeamsAPI, time_ranges: list) -> list:
    """
    Prepare the summary report.

    :param api: The Webex Teams API object.
    :param time_ranges: The time ranges to get the report for.
    :return: The prepared summary report, or an empty list if no report is found.
    """
    summary_report = []

    for range in time_ranges:
        summary_report.extend(get_recording_report(api, range[0], range[1]))

    return [] if not summary_report else summary_report


def recording_report_main(args: argparse.Namespace):
    detailed_report = []

    if args.period > 365 or args.span > 90:
        print(
            "Error: Invalid argument values. Please check the specified values for period and span."
        )
        sys.exit(1)

    token = get_token()

    api = WebexTeamsAPI(access_token=token)

    time_ranges = generate_time_ranges(total_days=args.period, span=args.span)

    summary_report = prepare_summary_report(api, time_ranges)

    if not summary_report:
        print("No recording report found.")
        sys.exit(0)

    for recording in summary_report:
        report = prepare_detailed_report_from_summary(api, recording)

        if not report:
            print(f"No detailed report found for {recording['recordingId']}")
            continue

        detailed_report.extend(report)

    if args.write:
        filename = write_csv(detailed_report, args.write)

        if filename:
            print("Report was saved to", filename)

    if os.getenv("VERBOSE") is not None:
        print(json.dumps(detailed_report, indent=4))


if __name__ == "__main__":
    args = parse_arguments()

    recording_report_main(args)
