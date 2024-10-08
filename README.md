# DynIP - Dynamic DNS Updater for Cloudflare

## Overview

DynIP is a Python-based application that automatically updates DNS records on Cloudflare when your public IP address changes. It's designed to run in a Docker container, making it easy to deploy and manage.

## Features

- Automatically detects changes in public IP address
- Updates A and CNAME records on Cloudflare
- Configurable update frequency
- Runs in a Docker container for easy deployment
- Logs all activities for monitoring and debugging

## Prerequisites

- Docker installed on your system
- A Cloudflare account with API access
- A domain managed by Cloudflare

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root with the following variables:

- `API_TOKEN`: Your Cloudflare API token with DNS edit permissions
- `ZONE_ID`: The Zone ID of your domain on Cloudflare
- `SLEEP_DURATION`: Time in seconds between IP checks (default: 30)

## Building the Docker Image

To build the Docker image:

```bash
docker build -t dynip-container -f .devcontainer/Dockerfile .
```

## Running the Container

To run the container:
```bash
docker run --env-file .env dynip-container
```
## Pushing to Docker Hub

To push your image to Docker Hub:
Tag your image:
```bash
docker tag dynip-container YOUR-DOCKER-HUB-USERNAME/dynip-container:latest
```
Push the image:
```bash
docker push YOUR-DOCKER-HUB-USERNAME/dynip-container:latest
```
## Script Details

The main script (dynip_script.py) performs the following actions:
- Retrieves the current public IP address
- Compares it with the last known IP address
- If changed, updates the specified DNS records on Cloudflare
- Logs all actions and results
- Waits for the specified duration before checking again

## Logging

The script logs all activities to stdout, which can be viewed using Docker logs:
```bash
docker logs [container_id]
```

## Customization

To change the domain or subdomains updated, modify the main() function in dynip_script.py
- Additional DNS record types can be supported by extending the create_or_update_dns_record() function

## Troubleshooting

If DNS updates fail, check your Cloudflare API token permissions
- Ensure your Cloudflare Zone ID is correct
- Verify that your domain is properly set up on Cloudflare

## Contributing
Contributions to DynIP are welcome! Please submit pull requests with any enhancements or bug fixes.
