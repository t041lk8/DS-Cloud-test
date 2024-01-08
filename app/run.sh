#!/bin/bash

set -e

if [ ! -f ./NERtagger/config.json ] || [ ! -f ./NERtagger/model.safetensors ]; then
    echo "Downloading weights..."
    wget --quiet https://github.com/t041lk8/DS-Cloud-test/releases/download/v0.0.1-dev/NERtagger.tar

    echo "Unboxing weights..."
    tar -xvf ./NERtagger.tar
else
    echo "Files exist."
fi

echo "starting app"
python3 ./main.py