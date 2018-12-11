#!/usr/bin/env python3
"""
This script substitutes any placeholders for production setup, i.e. authentication
tokens or URLs of services which differ from site to site.

All required values are expected to be found as environment variables or commandline
arguments, where the latter are having precedence, and the files requiring them can be
recognized by their *.in extension. This is required since not all services (especially
prometheus) support expanding environment variables inside their config files. Please do
not include any kind of quote, they will be stripped.
See `README.md` for an overview and how the services are communicating.
"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os import getenv
from string import Template
from pathlib import Path
from typing import Dict
from textwrap import indent, dedent

__author__ = "tluettje"
__license__ = "AGPLv3"

substitution_variables = {
    "PROMETHEUS_AUTH_TOKEN": {
        "description": """\
    The token used by the global/portal prometheus instance
    to authenticate itself against the HAProxy of the local/site prometheus
    instance."""
    },
    "SITE_NAME": {
        "description": """The name/location of site, should be unique among all sites."""
    },
    "SITE_PROMETHEUS_PROXY_URL": {
        "description": """\
    URL[:PORT] of the site proxy, which the global/portal prometheus will scrape."""
    },
    "INFLUXDB_ADMIN_USER": {
        "description": """\
        The name of the admin user of the influx database inside the portal""",
        "default": "admin",
    },
    "INFLUXDB_ADMIN_PASSWORD": {
        "description": """\
        The password of the admin user of the influx database inside the portal"""
    },
    "INFLUXDB_USER": {
        "description": """\
        The name of the user owning the database containing the prometheus data of the
        influx database inside the portal""",
        "default": "prometheus",
    },
    "INFLUXDB_USER_PASSWORD": {
        "description": """\
        The password of the user owning the database containing the prometheus data of
        the influx database inside the portal"""
    },
    "GF_SECURITY_ADMIN_USER": {
        "description": "The name of the grafana admin user inside the portal.",
        "default": "admin",
    },
    "GF_SECURITY_ADMIN_PASSWORD": {
        "description": "The password of the grafana admin user inside the portal."
    },
}

production_config_folder = Path(__file__).parent / "prod"


def main() -> int:
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog="{} @ {}".format(__license__, __author__),
    )
    template_args_parser = parser.add_argument_group("Template options")
    template_args_parser.add_argument(
        "-g",
        "--generate-template",
        action="store_true",
        help="""Print a sourcable file to STDOUT containing all variables to set with
        few defaults. Save it i.e. to `.env` (which is part of the gitignore)""",
    )
    build_args_parser = parser.add_argument_group("Build options")
    for var_name, var_information in substitution_variables.items():
        build_args_parser.add_argument(
            "--" + var_name,
            type=str,
            help=var_information["description"],
            default=getenv(var_name, ""),
        )
    build_args_parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Print built files instead of writing them.",
    )
    args = parser.parse_args()
    if args.generate_template:
        for var_name, var_information in substitution_variables.items():
            print(
                "{}\nexport {}={}".format(
                    # effectively replace any common whitespace at the beginning of
                    # every description line with '# '
                    indent(dedent(var_information["description"]), prefix="# "),
                    var_name,
                    var_information.get("default", ""),
                )
            )
        return 0
    else:
        return produce_config_files(vars(args), args.dry_run)


def produce_config_files(
    substitution_values: Dict[str, str], dry_run: bool = False
) -> int:
    if not production_config_folder.exists() and production_config_folder.is_dir():
        print(
            "Cannot find production folder at expected location `{}`. Aborting".format(
                production_config_folder
            )
        )
        return 1
    for variable in substitution_variables:
        if not substitution_values[variable]:
            print("Variable {} is empty. Aborting".format(variable))
            return 1

    for in_file in production_config_folder.glob("**/*.in"):
        print("Reading:", in_file)
        with in_file.open() as file:
            config_template = Template(file.read())
        try:
            config_out = config_template.substitute(substitution_values)
        except KeyError as e:
            print(
                "Missing value for variable {} in file `{}`. Aborting".format(
                    e.args, in_file
                )
            )
            return 1
        except ValueError as e:
            print("Could not process Template due to the following error:", e)
            return 2
        out_file = in_file.with_suffix("")
        if not dry_run:
            try:
                with out_file.open("w") as file:
                    file.write(config_out)
                print("Wrote constructed config to", out_file)
            except PermissionError as e:
                print("Could not save produced config, due to error:", e)
                return 2
        else:
            print("Output file: ", out_file, "\n", config_out)
    return 0


if __name__ == "__main__":
    exit(main())
