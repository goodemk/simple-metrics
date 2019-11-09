# simple-metrics
An experiment to implement a small monitoring stack by hand using statsd, Prometheus and Grafana.

## Architecture
The basis of this project is a small Python script that pulls information from running processes on the local host and sends that information to a Grafana dahboard by way of statsd and Prometheus. To make things more interesting, the script is designed to simulate the collection of metrics from any number of "hosts".

## Requirements
- Docker/docker-compose
- Python

## Installation
- In the project root directory, run `docker-compose up` to stand up statsd, Prometheus and Grafana.
- In the `/app/host` directory, run `python3 host_exporter.py`. By default, this will spawn one simulated host, pulling metrics from the local system. Use the `--hosts` flag to add more hosts.

## Viewing metrics

The RSS memory value is collected for each running process on the local host. statsd compiles the metrics into the following format: 

`statsclient.host0.1176.1626112|g`

The statsd-exporter then converts the metrics into a Prometheus-friendly format under the `host_process_memory` target:

`host_process_memory{host="host0",instance="host.docker.internal:9123",job="host_metrics",process="1176"}`

which, when queried, will return the corresponding memory value `1626112`.

### Prometheus
The web console is available at http://localhost:9090

### Grafana
The Grafana dashboard is available at [http://localhost:3000/](http://localhost:3000/d/6oafvFoWk/top-3-memory-consuming-processes?orgId=1&edit=true&from=1571169643918&to=1571170905974) with the default credentials (admin/admin). A sample dashboard shows the top 3 memory consumers over the last 5 minutes.
