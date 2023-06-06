FROM python:latest

WORKDIR /game

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "player_client.py"]