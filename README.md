# Openstack Projekt Monitoring

This repository contains the *docker-compose* scripts needed to setup a project-usage
monitoring system. See the graphic below to understand how all components interact with
each other.

![](overview.png)

One base idea is to use as much features of *Prometheus* as possible, namely its metrics
format and federation capabilities. Ideally every site (the deployment target of the
*Local-* Stack) with an OpenStack instance can reuse the local prometheus instance for
monitoring of additional services.

## Local-*

### Exporter

This is an [project usage exporter](https://github.com/gilbus/OS_project_usage_exporter)
with the ability to either serve real production data or fake data for
testing/development purposes. For more information see the linked repository.

### Prometheus & HAProxy

HAProxy is used to restrict the access of the *Portal-Prometheus* instance to the
`/federation` API. Since the organisations running the portal and the local site setup
might be different and in case the local prometheus instance is monitoring additional
services the local site might want to make all collected metrics available to the
portal. Therefore the request of the Portal-Prometheus is matched against a whitelisted
query.

Since Prometheus does not offer HTTP Authentication mechanism in terms of access control
but is able to provide
a [`bearer_token`](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#<scrape_config>)
when scraping targets the HAProxy only allows/forwards requests presenting the
configured token.

## Development Compose

```
docker-compose -f docker-compose.yml -f dev/docker-compose.override.yml up -d --build
```

This setup includes:

- 2 *Local-* Stacks according to the diagram above, the two
  [exporter](https://github.com/gilbus/OS_project_usage_exporter) are running in dummy
  mode
