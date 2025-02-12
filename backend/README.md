## Backend Structure

- `Backend`: The backend of the project
  - `service1`: Services for loaiding and performing tasks using the pre-trained models
    - `src`: Source file for all modules
      - `app.py`: The main python file that the docker container will run, every modules are called in this file
      - `Dockerfile`: Dockerfile will create the image in docker container which contains of all the installed packages and pre-trainded models
      - `requirements.txt`: this text file contains all the required python packages for running the pre-trained models
- `docker-compose.yml`: This file run all the services in the backend

## Models

### text-generation ()

## Quickstart with Docker

Run download_models.py to download STT/TSS/LLM models to correct folders.  

Ensure Docker is installed. In order to run the application, execute the following commands:

```bash
docker compose build app_linux
sudo docker compose run --rm --service-ports app_linux
```

Replace app_linux with app_windows or app_macos based on OS

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
