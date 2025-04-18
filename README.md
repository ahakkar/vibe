## Project Structure
- `.github/workflows`: Github Action workflow 
  - `tests.yml`: Github Action CI pipeline
- `src`: All the scripts of the backend and frontend
  - `backend`: The backend of the project
    - `app.py`: The main python file that the docker container will run, every modules are called in this file
    - `Dockerfile`: Dockerfile will create the image in docker container which contains of all the installed packages and pre-trainded models
    - `requirements.txt`: this text file contains all the required python packages for running the pre-trained models
    - `.env.default`: This is a default template for .env file which will be created when running the application
    - `local`: This contains all the modules and services for local application
      - `audio.py`: The audio service which uses to record the user's voice
      - `stt.py`: The speech to text service which transcribe user's voice to text
      - `text_gen.py`: The text generation service uses language model to generate texts
      - `tts.py`: The text to speech service which synthesize the generated text to voice output
      - `ir_service.py`: The intent recognition service which recognize user's intention in the sentence
      - `weather.py`: The weather service will provide the forecast of the weather in given location
      - `yle.py`: The YLE News service will provide news of the user's given topic
      - `cli.py`: The Command line service will run by the docker which runs the command line and provide all application's functionalities.
- `test`: Contains all the test files
- `docker-compose.yml`: This file run all the services in the backend and frontend
- `download_models.py`: This file download all the AI models for STT, TTS, and LLM
- `run.sh`: The bashscript used to download required dependencies and run the application

## Quickstart with Bash

Firstly, run the download_models.py to download all the models.

```bash
python download_models.py
```

Before running the application, create .env file and copy the .env.default content to .env in the same folder. 
Add YLE_APP_ID and YLE_APP_KEY.

Run run.sh file to download all necessary packages and run docker. 

```bash
./run.sh
```

## Quickstart with Docker

Run download_models.py to download STT/TSS/LLM models to correct folders.

Make sure Pipewire is installed and running on Linux.

Install Sox on Linux for efficient audio manipulation (changing sample rates)

Before running the application, create .env file and copy the .env.default content to .env in the same folder. 
Add YLE_APP_ID and YLE_APP_KEY.

Ensure Docker is installed. In order to run the application, execute the following commands:

```bash
docker compose build
docker compose run --rm --service-ports app
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

#### Run the application

Firstly, run the download_models.py to download all the models.

```bash
python download_models.py
```

Next, install the required python dependencies of backend using:

```bash
pip install -r src/backend/requirements.txt
```

Before running the application, create .env file and copy the .env.default content to .env in the same folder. 
Add YLE_APP_ID and YLE_APP_KEY.

Run the app.py with command line service option.

```bash
python src/backend/app.py --cli
```

#### Track the log to debug

There is a vibe.log file that will be created when the application run locally. 