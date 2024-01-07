FROM python:3.9.18-slim-bullseye

RUN apt-get -y update

RUN pip install tensorboard
WORKDIR /app

EXPOSE 6006
ENTRYPOINT tensorboard --logdir=model/lightning_logs --host 0.0.0.0 --port 6006