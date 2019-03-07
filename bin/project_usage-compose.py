#!/usr/bin/env python3
"""
Helper script to collect the different *.env files and prepare the docker-compose
call in production or dev mode, site and/or production part. Non `*.default.env` files
will be priorized and all unknown arguments will be appended to the docker-compose call,
i.e. `logs`, `start` ...
"""

import logging
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os import execve
from pathlib import Path
from shutil import which
from sys import argv
from typing import Dict

__author__ = "gilbus"
__license__ = "MIT"


docker_compose_path = which("docker-compose")
project_dir = Path(__file__).parent.parent

# mapping between default/example files and files with customized values
env_files = {
    project_dir / ".portal.default.env": project_dir / ".portal.env",
    project_dir / ".shared.default.env": project_dir / ".shared.env",
    project_dir / ".site.default.env": project_dir / ".site.env",
}

development_files = [
    project_dir / "docker-compose.site.yml",
    project_dir / "docker-compose.portal.yml",
    project_dir / "dev" / "docker-compose.override.yml",
]


def parse_env_files() -> Dict[str, str]:
    env = {}
    for default_file, custom_file in env_files.items():
        env_file = default_file
        if custom_file.exists():
            logging.debug(
                "Reading %s instead of default file %s".format(
                    custom_file, default_file
                )
            )
            env_file = custom_file
        else:
            logging.debug("Reading default file %s", default_file)
        for line in env_file.read_text().splitlines():
            if not line.strip() or line.strip().startswith("#"):
                continue
            try:
                key, value = line.split("=")
            except ValueError:
                logging.warning(
                    "`{}` is not valid, to set a variable with an empty value append "
                    "a `=`, i.e. `USAGE_EXPORTER_PROJECT_DOMAINS=`".format(line)
                )
                continue
            env.update({key: value})
    return env


def main() -> int:

    parser = ArgumentParser(
        description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog="{} @ {}".format(__license__, __author__),
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase verbosity"
    )

    subparsers = parser.add_subparsers(
        title="Subcommands", description="Different launch modi", dest="subcommand"
    )

    dev_parser = subparsers.add_parser(
        "development",
        aliases=["dev"],
        description="""Run the whole `project_usage` in development mode. Usage data
        from multiple sites will be emulated by the exporter services, collected by the
        `site_*` services. The `portal_prometheus` will scrape their data, store then
        inside the InfluxDB which will make them accessible to the `credits`
        service. All Prometheus and Grafana instances are launched with port mappings.""",
    )

    print_env_parser = subparsers.add_parser(
        "print-env",
        aliases=["env"],
        description="""Print the parsed environment variables, can be used to export it
        into the current shell by `export $({} print-env | xargs)""".format(
            argv[0]
        ),
    )
    print_env_parser.add_argument(
        "-s", "--separator", default="\n", help="Separator between `key=value` pairs"
    )

    args, remaining_args = parser.parse_known_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.debug(
        "Known command line arguments: %s, Remainder: %s", args, remaining_args
    )
    if not docker_compose_path:
        logging.critical("Could not detect `docker-compose` in $PATH. Exiting")
        return 1

    if "env" in args.subcommand:
        print(
            args.separator.join(
                "{key}={value}".format(
                    key=key, value="'{}'".format(value) if value else ""
                )
                for key, value in parse_env_files().items()
            )
        )
        return 0
    if "dev" in args.subcommand:
        call = [docker_compose_path]
        for file in development_files:
            call.extend(("-f", str(file)))
        call.extend(remaining_args)
        env = parse_env_files()
        logging.debug("Executing %s with environment %s", call, env)
        execve(docker_compose_path, call, env)

    return 0


if __name__ == "__main__":
    exit(main())
