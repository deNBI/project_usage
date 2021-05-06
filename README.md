# Openstack Projekt Monitoring

This repository contains the *docker-compose* scripts needed to setup a project-usage
monitoring system. See the <a href="../../wiki/">wiki</a> for a graphical visualization how
the services interact with each other and more documentation.

# Set up develop stack

## Requirements
Clone this repo. If you want to use exporter and credits container you build locally, also clone the 
[OS_project_usage_exporter repo](https://github.com/deNBI/OS_project_usage_exporter) and the 
[os_credits repo](https://github.com/deNBI/os_credits).

## Set up environment
### .site.env
Go to your cloned project_usage repository and copy the .site.default.env to .site.env.
```bash
cp .site.default.env .site.env
```
Open the .site.env file and fill out the environment variables as you need them. You can see the variable descriptions 
[here](https://github.com/deNBI/OS_project_usage_exporter#usage).  

**Important**: The `USAGE_EXPORTER_START_DATE_ENDPOINT` is defined by default to get data from an active endpoint. 
You need to have the Cloud-API running and adjust the endpoint to point to localhost, otherwise the exporter will not start. 
If you do not want to use an active endpoint, uncomment the variable and use the `USAGE_EXPORTER_START_DATE` variable.  

If you want to fetch mb and vcpu weights from an active endpoint instead of the dev//dummy_files/dummy_weights.toml, you 
need to open the dev/docker-compose.override.yml, remove the `USAGE_EXPORTER_DUMMY_WEIGHTS_FILE=dummy_weights.toml` entry in 
the environment in the site_exporter service and add `USAGE_EXPORTER_WEIGHTS_UPDATE_ENDPOINT` and adjust it in your .site.env
to point to your localhost endpoint.
### .portal.env (If you want to write usage data to perun)
Go to your cloned project_usage repository and copy the .portal.default.env to .portal.env.
```bash
cp .portal.default.env .portal.env
```
Here you need to adjust the perun login data you find under `#credits`.

If you want to simulate and observe the usage for a specific project, create the project if it does not already exist 
and visit [perun](https://perun.elixir-czech.cz/). Add the group to the `8676 - test-credit-resource`.  
Open the dev/dummy_cc.toml file and adjust it accordingly. In the default.projects section you will find examples for 
openstack projects and in the elixir.projects.machines sections you will find examples for simplevm projects.
## Stack usage with pre-build container from docker hub
### Start the stack
Go to your project_usage repository and run:
```bash
bin/project_usage-compose.py dev up --detach
```
### Stop the stack
Go to your project_usage repository and run:
```bash
bin/project_usage-compose.py dev down
```

## Stack usage with locally build container
### Start the stack
Copy your .shared.default.env to .shared.env:
```bash
cp .shared.default.env .shared.env
```

Here you will see the variables `DEV_EXPORTER_SITE_*` and `DEV_OS_CREDITS`. Uncomment the variables with the `denbicloud/` argument
if you want to use pre-build container, uncomment the variables without the `denbicloud/` argument if you want to use locally build
container! **By default, the pre-build container arguments are uncommented!**
#### os_project_usage_exporter
Go to your OS_project_usage_exporter repository and run:
```bash
docker build -f Dockerfile -t os_project_usage_exporter .
```
#### os_credits
**If you want to use the live reloading dev version you need to adjust the .default.env in your os_credits repository:**
Go to your cloned os_credits repository and copy the .default.env to .env.  
```bash
cp .default.env .env
```
Open the .env file and fill out the perun login information.
If you do not want to use the live reloading dev version but still want to use a local build container, you will not need
the .env from your os_credits repository.
In your os_credits repository run:
```bash
make docker-build-dev
```

Go to your project_usage repository and run:
```bash
bin/project_usage-compose.py dev up --detach
```

If you now want to use the live reloading os_credits container, go back to your os_credits repository and run:
```bash
make docker-project_usage-dev
```

### Stop and remove the stack
Go to your project_usage repository and run:
```bash
bin/project_usage-compose.py dev down
```

If you have a live reloading os_credits container running, you will need to stop and remove the portal_credits container
manually:
```bash
docker stop portal_credits
docker rm portal_credits
```
