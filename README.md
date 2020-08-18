# Openstack Projekt Monitoring

This repository contains the *docker-compose* scripts needed to setup a project-usage
monitoring system. See the <a href="../../wiki/">wiki</a> for a graphical visualization how
the services interact with each other and more documentation.

# Set up develop stack

## Requirements
Clone this repo, the [OS_project_usage_exporter repo](https://github.com/deNBI/OS_project_usage_exporter) and the 
[os_credits repo](https://github.com/deNBI/os_credits).

### Set up environment
#### os_credits
Go to your cloned os_credits repository and copy the .default.env to .env.  
```bash
cp .default.env .env
```
Open the .env file and fill out the perun login information.
#### project_usage
Go to your cloned project_usage repository and copy the .site.default.env to .site.env.
```bash
cp .site.default.env .site.env
```
Open the .site.env file and fill out the environment variables as you need them. You can see the variable descriptions 
[here](https://github.com/deNBI/OS_project_usage_exporter#usage).  

If you want to fetch mb and vcpu weights from an active endpoint instead of the dev/dummy_weights.toml, you need to 
open the dev/docker-compose.override.yml, remove the `USAGE_EXPORTER_DUMMY_WEIGHTS_FILE=/dummy_weights.toml` entry in 
the environment in the site_exporter service and add `USAGE_EXPORTER_WEIGHTS_UPDATE_ENDPOINT`.
#### Simulate usage for real projects
If you want to simulate and observe the usage for a specific project, create the project if it does not already exist 
and visit [perun](perun.elixir-czech.cz/). Add the group to the `8676 - test-credit-resource`. Open the dev/dummy_cc.toml
file and adjust it accordingly. In the default.projects section you will find examples for openstack projects and in the
elixir.projects.machines sections you will find examples for simplevm projects.
## Starting the stack
Go to your OS_project_usage_exporter repository and run:
```bash
docker build -f Dockerfile -t os_project_usage_exporter .
```

Go to your OS_credits repository and run:
```bash
make docker-build-dev
```

Go to your project_usage repository and run:
```bash
bin/project_usage-compose.py dev up --detach
```

After the containers are running, go back to your OS_credits repository and run:
```bash
make docker-project_usage-dev
```

## Stop the stack
Go to your project_usage repository and run:
```bash
bin/project_usage-compose.py dev down
docker stop portal_credits
docker rm portal_credits
```
