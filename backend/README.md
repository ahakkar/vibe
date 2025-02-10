## Backend Structure
- `Backend`: The backend of the project
    - `service1`: Services for loaiding and performing tasks using the pre-trained models
        - `src`: Source file for all modules 
            - `app.py`: The main python file that the docker container will run, every modules are called in this file
            - `Dockerfile`: Dockerfile will create the image in docker container which contains of all the installed packages and pre-trainded models
            -  `requirements.txt`: this text file contains all the required python packages for running the pre-trained models
- `docker-compose.yml`: This file run all the services in the backend

## Models
### text-generation ()

## Docker Installation
Ensure Docker is installed. In order to run Docker, executes these following commands:
```bash
docker-compose build
docker-compose up
``` 
The server will be accessible at http://127.0.0.1:5000/

### Local Installation
*Prerequisites:* Python 3.9 & Pip

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