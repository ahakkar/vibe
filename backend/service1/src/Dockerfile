FROM python:3.9

WORKDIR /usr/src/

COPY requirements.txt ./

RUN apt-get update && apt-get install -y portaudio19-dev 
RUN apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl-doc libportaudio2
RUN apt-get install -y pulseaudio
RUN apt-get install -y alsa-utils

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# For window user using pulseaudio to connect with Docker container output audio
ENV PULSE_SERVER=host.docker.internal 

EXPOSE 5000

CMD ["python", "app.py"]
