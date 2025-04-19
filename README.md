## Backend Structure

- `Backend`: The backend of the project
  - `service1`: Services for loaiding and performing tasks using the pre-trained models
    - `src`: Source file for all modules
      - `app.py`: The main python file that the docker container will run, every modules are called in this file
      - `Dockerfile`: Dockerfile will create the image in docker container which contains of all the installed packages and pre-trainded models
      - `requirements.txt`: this text file contains all the required python packages for running the pre-trained models
- `docker-compose.yml`: This file run all the services in the backend

## Quickstart with Bash

Run run.sh file to download all the packages

```bash
./run.sh
```

## Quickstart with Docker

Run download_models.py to download STT/TSS/LLM models to correct folders.

Make sure Pipewire is installed and running on Linux.

Install Sox on Linux for efficient audio manipulation (changing sample rates)

Ensure Docker is installed. In order to run the application, execute the following commands:

```bash
docker compose build
sudo docker compose run --rm --service-ports app
```

You can try running "sudo modprobe uinput" if there's problems, delete this line if not needed

## Run Docker CLI

Ensure that docker image was built by execute this command:

```bash
docker images
```

Run the image with the image id or name, execute this command:

```bash
docker run -it image_name
```

To go inside docker shell, execute this command:

```bash
docker run -it image_name /bin/bash
```

## Run Docker CLI with performance recording

Note that starting and stopping the application takes time due to logging processes

```bash
docker compose run --rm --service-ports  \
  --volume /tmp/perf_data:/perf_data \
  --entrypoint perf \
  app \
  record -F 100 --call-graph dwarf \
  --output /perf_data/perf.data \
  -- python app.py --cli
```

Perf data is saved to host's /tmp/perf_data/perf.data file and it can be analysed with hotspot
```bash
sudo chown $USER:$USER /tmp/perf_data/perf.data
sudo apt install hotspot
hotspot /tmp/perf_data/perf.data 
```

### Local Installation

_Prerequisites:_ Python 3.9 & Pip

#### Environment Setup

Create a virtual environment:

```bash
python -m venv env
```

- On Linux/Mac, activate the environment with:

```bash
source env/bin/activate
```

- On Windows, activate the environment with:

```bash
.\env\Scripts\activate
```

- On git bash, activate the environment with:

```bash
source env/Scripts/activate
```

Next, install the required python dependencies using:

```bash
pip install -r requirements.txt
```
