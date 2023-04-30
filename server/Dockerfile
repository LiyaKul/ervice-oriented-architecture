FROM python:latest

WORKDIR /server

ENV PORT=2001

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "-u", "server.py"]