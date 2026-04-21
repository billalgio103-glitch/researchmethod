FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    openpyxl==3.1.5 \
    pandas==2.2.3 \
    matplotlib==3.9.4 \
    scipy==1.14.1 \
    numpy==2.1.3

WORKDIR /work
