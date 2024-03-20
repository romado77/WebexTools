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

> --file FILE, -f FILE CSV _File with users data_
>
> --column COLUMN, -c COLUMN _Column name for user email_
>
> --report, -r _Save the report to the file_
>
> --verbose, -v _Verbose output_

### Example of CSV file:

```csv
First Name,Last Name,Display Name,User ID/Email (Required),User Status,...
Test,User,Test User,test@test.com,Active,...
```

#### Note:

> Only column with user email is required in the CSV file, all other columns are optional and will be ignored.

### Example of run command:

```sh

webextools disable-users -f users.csv -c "User ID/Email (Required)" -r -v

```

#### Notes:

> The `-c` option can be omitted if the column containing email addresses in the CSV file is named `email`.
>
> If the `-r` option is provided, the report for each operation will be saved to a file named `disabled_users_report-{datetime}.json` in current directory.
>
> If the `-v` option is provided, verbose output will be enabled and each user operation will be printed to the console.

## 2. Recording audit report

The Recording Audit Reporting Tool provides an audit report for Webex recordings over a specified period.
You can customize the reporting period and save the results to a CSV file.
This tool is ideal for monitoring and analyzing recording activities.

### Usage:

```bash
webextools recording-report
```

#### Run options:

> --period PERIOD, -p PERIOD _Recording report period in days (default 90 days, max 365 days)_
>
> --write FILENAME, -w FILENAME _Specify the file name to write the report_
>
> --verbose, -v _Verbose output_

### Example of run command:

```sh
webextools recording-report -p 90 -w report -v
```

#### Notes:

> Option `-p 90` specifies the period of the report in days. The default value is 90 days, so it could be omitted.
>
> Option `-s 7` specifies the span of the report in days. The default value is 7 days, so it could be omitted.
>
> Option `-w report` specifies the file name to write the report. Report format is CSV and extension `csv` can be omitted.
>
> If option `-v` presents, report will be printed to the console.
