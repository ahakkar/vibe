FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir torch==2.5.1 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
