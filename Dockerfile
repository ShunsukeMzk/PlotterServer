FROM python:3.9 AS builder

RUN apt-get update -qq && apt-get install -y vim less
COPY requirements.txt ./requirements.txt
RUN pip install --requirement requirements.txt
