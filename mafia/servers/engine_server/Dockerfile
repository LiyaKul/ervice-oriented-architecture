FROM python:latest

WORKDIR /game

ENV PORT=51075

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "server.py"]