# CatCam

## Project Overview

DETECT CATS :D

## Environment Setup

Our uses Docker to simplify environment setup. You will need both `docker` and `docker-compose` (or `podman` and `podman-compose`).

### Install Docker

Please follow Docker's official guide to install Docker: <https://docs.docker.com/engine/install>

Additionally, follow their guide on installing `docker-compose`: <https://docs.docker.com/compose/install>

### (Alternative) Install Podman

> If you are using Windows, it is recommended to use WSL when using podman.

Follow Podman's guide to install podman: <https://podman.io/docs/installation>

To install podman compose, run the following (`apt`/`pipx` installation):

```bash
sudo apt install pipx
pipx install podman-compose
```

> **NOTE:** If you are using podman, replace all `docker` commands with `podman` and all `docker-compose` commands with `podman-compose`.

### Build Containers

Once Docker is installed, you may build the containers with this command (execute from the root directory of the repository):

```bash
docker-compose build
```

## Running the Code

To run the entire app at once, simply use:

```bash
docker-compose up -d
```

To stop the app, run:

```bash
docker-compose down
```

To run a specific service, use the following:

```bash
docker-compose run --rm -d <service_name>
```

> If you would like to automatically attach to the container, remove the `-d` flag from the above command.

The available services are `frontend` and `backend`.

## Overriding `docker-compose.yml`

If you need to modify the parameters used to run the containers, do not directly modify `docker-compose.yml`. Instead, create a file called `docker-compose.override.yml`. Any parameters put into this file will override the parameters in `docker-compose.yml`.

If you wish to use the containers to assist with development, you may use the pre-existing override file provided in `/dockerTemplates`:

```bash
cp ./dockerTemplates/dev-override.yml ./docker-compose.override.yml
```
