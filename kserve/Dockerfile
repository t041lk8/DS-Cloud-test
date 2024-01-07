FROM python:3.9.18-slim-bullseye

RUN apt-get -y update

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install numpy kserve transformers
WORKDIR /app

COPY ./app.py .