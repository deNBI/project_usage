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

You can also use copy the .site.dev.env to .env instead, which is initialized for a dev environment where the API is running 
with weights and a startdate.

**On start date:**  
The `USAGE_EXPORTER_START_DATE_ENDPOINT` is defined by default to get data from an active endpoint.  
You need to have the Cloud-API running and adjust the endpoint to point to dockerhost, otherwise the exporter will not start. 
If you do not want to use an active endpoint, uncomment in `dev/docker-compose.override.yml` the environment variable 
`- USAGE_EXPORTER_START_DATE`, in your `.site.env` uncomment the `USAGE_EXPORTER_START_DATE` variable and 
comment the `USAGE_EXPORTER_START_DATE_ENDPOINT`.  

**On weights:**  
The `USAGE_EXPORTER_WEIGHTS_UPDATE_ENDPOINT` is defined by default to get data from an active endpoint.  
You need to have the Cloud-API running and adjust the endpoint to point to dockerhost, otherweise the weights will be 
initialized with value 1.  
If you do not want to use an active endpoint, uncomment in `dev/docker-compose.override.yml` the environment variable
`- USAGE_EXPORTER_DUMMY_WEIGHTS_FILE=/dummy_weights.toml`.

**On projects:**  
In the `dev/dummy_files` folder you will find multiple `dummy_cc_site_* toml files`. In `dummy_cc_site_b.toml` 
you will find an overview on how to configure a toml file for SimpleVM projects and Openstack projects.  
The `dummy_cc_site_a.toml.2000` and `*.10000` are desgined to stress test the stack with 2000, respectively 10000, projects.  
The `dummy_cc_site_a.toml.1` contains exactly one project.  
To change which toml will be read by the exporter, go to `dev/docker-compose.override.yml` and change the 
`- "./dev/dummy_files/dummy_cc_site_a.toml.1:/dummy_cc.toml"` value.
To test the credits stack with a project running in your dev environment, change the `project_name` in your chosen toml file 
to the shortname of the project you want to test it with.

### .portal.env
Go to your cloned project_usage repository and copy the .portal.default.env to .portal.env.
```bash
cp .portal.default.env .portal.env
```

If you want os_credits to communicate with the protected Cloud-API endpoints, you need to set an api key in the admin overview 
of the running Cloud-API and set it under the `API_CONTACT_KEY` variable.  

## Use pre-build container from docker hub
**Exporter:**  
Go to your `.shared.env` and make sure you uncomment the `DEV_EXPORTER_SITE_*=denbicloud/os_project_usage_exporter:dev` 
variables und comment the `DEV_EXPORTER_SITE_A=os_project_usage_exporter:latest` variables.  

**Os_credits:**  
Go to your `.shared.env` and make sure you uncomment the `DEV_OS_CREDITS=denbicloud/os_credits:dev`
variable, comment the `DEV_OS_CREDITS=os_credits-dev:latest` variable. Also go to the `dev/docker-compose.override.yml` and 
make sure you comment the volume `- ${CREDITS_SRC_FILE_PATH}:${CREDITS_SRC_DEST}:ro`.

### Start the stack
Go to your project_usage repository and run:
```bash
make up-dev
```
### Stop the stack
Go to your project_usage repository and run:
```bash
make down-dev
```

## Use locally build container
**Exporter:**  
In your OS_project_usage_exporter repository run:
```bash
docker build -f Dockerfile -t os_project_usage_exporter .
```

Go to your `.shared.env` and make sure you comment the `DEV_EXPORTER_SITE_*=denbicloud/os_project_usage_exporter:dev`
variables und uncomment the `DEV_EXPORTER_SITE_A=os_project_usage_exporter:latest` variables.

**Os_credits:**  
In your os_credits repository run:
```bash
make docker-build-dev
```
Go to your `.shared.env` and make sure you comment the `DEV_OS_CREDITS=denbicloud/os_credits:dev`
variable, uncomment the `DEV_OS_CREDITS=os_credits-dev:latest`, `CREDITS_SRC_FILE_PATH` (and adjust it to point to your 
`.../os_credits/src` folder) and `CREDITS_SRC_DEST` variables. Also go to the `dev/docker-compose.override.yml` and
make sure you uncomment the volume `- ${CREDITS_SRC_FILE_PATH}:${CREDITS_SRC_DEST}:ro`.

### Start the stack
Go to your project_usage repository and run:
```bash
make up-dev
```

### Stop and remove the stack
Go to your project_usage repository and run:
```bash
make down-dev
```
