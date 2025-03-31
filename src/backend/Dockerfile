FROM python:3.9

WORKDIR /usr/src/

COPY requirements.txt ./

RUN apt-get update && apt-get install -y portaudio19-dev sox libsox-fmt-all
RUN apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl-doc libportaudio2
RUN apt-get install -y pipewire pipewire-audio-client-libraries libspa-0.2-bluetooth pipewire-pulse pipewire-alsa alsa-utils
RUN apt-get update && apt-get install -y libvoikko-dev

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables for PipeWire
ENV PIPEWIRE_SERVER=unix:/run/user/1000/pipewire-0

EXPOSE 5000

CMD ["python", "app.py", "--cli"]
