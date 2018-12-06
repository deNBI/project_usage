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

__author__ = "tluettje"
__license__ = "AGPLv3"

substitution_variables = {
    "PROMETHEUS_AUTH_TOKEN": """The token used by the global/portal prometheus instance
    to authenticate itself against the HAProxy of the local/site prometheus
    instance.""",
    "SITE_PROMETHEUS_PROXY_URL": """URL[:PORT] of the site proxy, which the
    global/portal prometheus will scrape.""",
    "SITE_NAME": """The name/location of site, should be unique among all sites.""",
}

production_config_folder = Path(__file__).parent / "prod"


def main() -> int:
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog="{} @ {}".format(__license__, __author__),
    )
    for var, description in substitution_variables.items():
        parser.add_argument(
            "--" + var, type=str, help=description, default=getenv(var, "")
        )

    args = parser.parse_args()
    substitution_values = vars(args)
    if not production_config_folder.exists() and production_config_folder.is_dir():
        print(
            "Cannot find production folder at expected location `{}`. Aborting".format(
                production_config_folder
            )
        )
        return 1
    for key, value in substitution_values.items():
        if not value:
            print('Variable {} is empty. Aborting'.format(key))
            return 1

    for in_file in production_config_folder.glob("**/*.in"):
        print("Reading:", in_file)
        with in_file.open() as file:
            config_template = Template(file.read())
        try:
            config_out = config_template.substitute(substitution_values)
        except KeyError as e:
            print("Missing value for variable {}. Aborting".format(e.args))
            return 1
        except ValueError as e:
            print("Could not process Template due to the following error:", e)
            return 2
        out_file = in_file.with_suffix("")
        try:
            with out_file.open("w") as file:
                file.write(config_out)
            print("Wrote constructed config to", out_file)
        except PermissionError as e:
            print("Could not save produced config, due to error:", e)
    return 0


if __name__ == "__main__":
    exit(main())
