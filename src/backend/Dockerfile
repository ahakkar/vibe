FROM python:3.9

WORKDIR /usr/src/

COPY requirements.txt ./

RUN mkdir /usr/src/logs
RUN mkdir -p chroma_db && chmod a+rwx -R chroma_db

RUN apt-get update && apt-get install -y \
    build-essential linux-perf  \
    portaudio19-dev libportaudio2 sox libsox-fmt-all \
    pipewire pipewire-audio-client-libraries pipewire-pulse pipewire-alsa alsa-utils \
    libvoikko1 voikko-fi libvoikko-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables for PipeWire
ENV PIPEWIRE_SERVER=unix:/run/user/1000/pipewire-0

EXPOSE 5000

CMD ["python", "app.py", "--cli"]
