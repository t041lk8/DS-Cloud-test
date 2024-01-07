FROM python:3.9.18-slim-bullseye

RUN apt-get -y update

RUN pip install jupyterlab
WORKDIR /app

EXPOSE 8888
ENTRYPOINT jupyter lab --ip=0.0.0.0 --allow-root --port=8888 --NotebookApp.token='' --NotebookApp.password=''