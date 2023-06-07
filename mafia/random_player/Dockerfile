FROM python:latest

WORKDIR code/

COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python3", "random_player.py"]