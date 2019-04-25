#!/usr/bin/env python3
"""
Helper script to collect the different *.env files and prepare the docker-compose call
in production or dev mode, site and/or production part. Non `*.default.env` files will
be prioritized and all unknown arguments will be appended to the docker-compose call,
i.e. `logs`, `start` ...
"""

import logging
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os import environ, execve
from pathlib import Path
from shutil import which
from string import Template
from sys import argv
from typing import Dict, List, Mapping

__author__ = "gilbus"
__license__ = "MIT"


docker_compose_path = which("docker-compose")
project_dir = Path(__file__).parent.parent
dev_dir = project_dir / "dev"
prod_dir = project_dir / "prod"
staging_dir = project_dir / "staging"
staging_dev_dir = project_dir / "staging-dev"

shared_env_file = {project_dir / ".shared.default.env": project_dir / ".shared.env"}
# mapping between default/example files and files with customized values
env_files = {
    "portal": {
        project_dir / ".portal.default.env": project_dir / ".portal.env",
        **shared_env_file,
    },
    "site": {
        project_dir / ".site.default.env": project_dir / ".site.env",
        **shared_env_file,
    },
    "staging": {project_dir / ".staging.default.env": project_dir / ".staging.env"},
}

development_files = [
    project_dir / "docker-compose.site.yml",
    project_dir / "docker-compose.portal.yml",
    dev_dir / "docker-compose.override.yml",
]

prod_files = {
    "portal": [
        project_dir / "docker-compose.portal.yml",
        prod_dir / "docker-compose.portal.override.yml",
    ],
    "site": [
        project_dir / "docker-compose.site.yml",
        prod_dir / "docker-compose.site.override.yml",
    ],
}
staging_files = {
    "portal": [staging_dir / "docker-compose.portal.override.yml"],
    "site": [staging_dir / "docker-compose.site.override.yml"],
}
staging_dev_files = {
    "portal": [staging_dev_dir / "docker-compose.portal.override.yml"],
    "site": [staging_dev_dir / "docker-compose.site.override.yml"],
}

# staging and dev should never need template files
staging_template_files = {
    # given without 'prod' or 'staging' and assuming that the internal file structure is
    # the same
    "portal": [Path("portal_prometheus") / "prometheus.yml.in"],
    # no template files currently, can all be done at runtime via env vars
    "site": [],
}  # type: Dict[str, List[Path]]


def parse_env_files(env_files: Dict[Path, Path]) -> Dict[str, str]:
    env = {}
    for default_file, custom_file in env_files.items():
        env_file = default_file
        if custom_file.exists():
            logging.debug(
                "Reading %s instead of default file %s", custom_file, default_file
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


def format_env(env: Mapping[str, str], separator: str = "\n") -> str:
    return separator.join(
        "{key}={value}".format(key=key, value="'{}'".format(value) if value else "")
        for key, value in env.items()
    )


def main() -> int:

    parser = ArgumentParser(
        description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog="{} @ {}".format(__license__, __author__),
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase verbosity"
    )
    parser.add_argument(
        "-k",
        "--keep-env",
        action="store_true",
        help="Do not parse any *.env files, only use existing environment variables.",
    )

    subparsers = parser.add_subparsers(
        title="Subcommands", description="Different launch modi", dest="subcommand"
    )

    subparsers.add_parser(
        "dev",
        description="""Run the whole `project_usage` in development mode. Usage data
        from multiple sites will be emulated by the exporter services, collected by the
        `site_*` services. The `portal_prometheus` will scrape their data, store then
        inside the InfluxDB which will make them accessible to the `credits`
        service. All Prometheus and Grafana instances are launched with port mappings.""",
    )

    prod_parser = subparsers.add_parser(
        "prod",
        description="""Run either the `site` or the `portal` stack in production mode.""",
    )
    prod_parser.add_argument("stack", choices=("portal", "site"))
    staging_args = prod_parser.add_mutually_exclusive_group()
    staging_args.add_argument(
        "--staging",
        action="store_true",
        help="""Start services in staging mode. See .staging.default.env and staging/ to
        see additional settings and config files. Used in staging area where site and
        portal stack are running on the same machine, but the exporter is connected to a
        real OpenStack instance. The external network `portal_default` is required where
        a separate HAProxy ought to provide access to `portal_prometheus` and
        `portal_grafana`""",
    )
    staging_args.add_argument(
        "--staging-dev",
        action="store_true",
        help="""Same as staging but for deploying to the local machine. An additional
        network called 'fake_internet' is needed to connect the site_prometheus_proxy
        and the portal_prometheus instance to emulate the public network. Create it via
        `docker network create fake_internet`""",
    )

    non_docker_actions = parser.add_mutually_exclusive_group()

    non_docker_actions.add_argument(
        "-p",
        "--print-env",
        action="store_true",
        help="""Print the parsed environment variables separated by newline, can be
        used to export it into the current shell by `export $({} print-env |
        xargs)`""".format(
            argv[0]
        ),
    )
    non_docker_actions.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Do not exec docker-compose, only print call.",
    )

    args, remaining_args = parser.parse_known_args()
    if not args.subcommand:
        print("Please choose a subcommand.")
        parser.print_help()
        return 2
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
    call = [docker_compose_path]

    if "dev" == args.subcommand:
        needed_compose_files = development_files
        needed_env_files = {**env_files["portal"], **env_files["site"]}
        template_files_dir = project_dir / "dev"
    else:
        needed_compose_files = prod_files[args.stack]
        needed_env_files = env_files[args.stack]
        template_files_dir = project_dir / "prod"
        if args.staging:
            needed_compose_files.extend(staging_files[args.stack])
            needed_env_files.update({**env_files["staging"]})
            # Currently only 'prometheus.yml.in' therefore only `staging/` has to be
            # checked
            template_files_dir = project_dir / "staging"
        elif args.staging_dev:
            needed_compose_files.extend(staging_dev_files[args.stack])
            needed_env_files.update({**env_files["staging"]})
            template_files_dir = project_dir / "staging-dev"

    if args.keep_env:
        env = environ
    else:
        env = {**environ, **parse_env_files(needed_env_files)}  # type: ignore
    if args.print_env:
        print(format_env(env))
        return 0
    for file in needed_compose_files:
        call.extend(("--file", str(file)))
    call.extend(remaining_args)
    if args.dry_run:
        print(" ".join(call))
        return 0
    if args.subcommand == "prod" and (args.staging or args.staging_dev):
        for file in staging_template_files[args.stack]:
            template_file = template_files_dir / file
            out_file = template_file.with_suffix("")
            # if out_file.exists():
            #    continue
            logging.warning("Formatting needed template file %s", template_file)
            template = Template(template_file.read_text())
            try:
                out_file_str = template.substitute(env)
            except ValueError as e:
                logging.error("Invalid template file, error %s", e)
                return 1
            except KeyError as e:
                logging.error("Missing value for key %s. Aborting", e)
                return 1
            logging.info("Saving formatted file to %s", out_file)
            out_file.write_text(out_file_str)

    logging.debug("Executing %s with environment %s", call, env)
    execve(docker_compose_path, call, env)

    return 0


if __name__ == "__main__":
    exit(main())
