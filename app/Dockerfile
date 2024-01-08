FROM python:3.9.18-slim-bullseye

RUN apt update && \
    apt install -y wget

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install kserve transformers

WORKDIR /app
COPY ./ ./

RUN chmod +x ./run.sh

ENTRYPOINT ["/bin/bash", "run.sh"]