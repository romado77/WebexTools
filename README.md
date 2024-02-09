# WebexTools

WebexTools is a collection of command-line tools designed to simplify operational tasks and streamline bulk actions in Cisco Webex.

## Installation

To use WebexTools, follow the installation instructions below.

```sh

pip install git+https://github.com/romado77/WebexTools.git

```

## Webex API Token

You need to have a Webex API token to use WebexTools. You can obtain a token by following the instructions in the [Webex API documentation](https://developer.webex.com/docs/api/getting-started).

To use the token, you can set the environment variable `WEBEX_TEAMS_ACCESS_TOKEN`. If environment variable is not set, you will be prompted to enter it when running the tool.

# Available Tools

## 1. Disable users

The User Disabling Tool allows you to disable Webex users based on the information provided in a CSV file.
This tool is useful for managing user access in bulk.

### Usage:

```sh
webextools disable-users
```

#### Run options:

> --file FILE, -f FILE CSV _file with users data_
>
> --column COLUMN, -c COLUMN _Column name to use for user email_
>
> --report, -r _Write the report to the file_
>
> --verbose, -v _Verbose output_

### Example of CSV file:

```csv
email,username
test@test.com,Test User
```

### Example of run command:

```sh

webextools disable-users -f users.csv -c email -r -v

```

#### Notes:

> Option `-c email` could be omitted if the column name with email addresses, in CSV file, is `email`
>
> If option `-r` presents, report, for each operation, will be saved to the file `disabled_users_report-{datetime}.json` in current directory.
>
> If option `-v` presents, verbose output will be enabled and each user operation will be printed to the console.

## 2. Recording audit report

The Recording Audit Reporting Tool provides an audit report for Webex recordings over a specified period.
You can customize the reporting period and save the results to a JSON file.
This tool is ideal for monitoring and analyzing recording activities.

### Usage:

```bash
webextools recording-report
```

#### Run options:

> --period PERIOD, -p PERIOD _Recording report period in days (default 90 days, max 365 days)_
>
> --span SPAN, -s SPAN _Recording report span in days (default 7 days, max 90 days)_
>
> --write FILENAME, -w FILENAME _Specify the file name to write the report_
>
> --verbose, -v _Verbose output_

### Example of run command:

```sh
webextools recording-report -p 90 -s 7 -w report -v
```

#### Notes:

> Option `-p 90` specifies the period of the report in days. The default value is 90 days, so it could be omitted.
>
> Option `-s 7` specifies the span of the report in days. The default value is 7 days, so it could be omitted.
>
> Option `-w report` specifies the file name to write the report. Report format is CSV and extension `csv` can be omitted.
>
> If option `-v` presents, report will be printed to the console.
