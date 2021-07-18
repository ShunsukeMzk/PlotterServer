FROM python:3.9 AS builder

RUN apt-get update -qq && apt-get install -y vim less
COPY requirements.txt ./requirements.txt
RUN pip install --requirement requirements.txt

FROM python:3.9-slim

SHELL ["/bin/bash", "-c"]
RUN apt-get update -qq && apt-get install -y vim less
WORKDIR /work
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . .
RUN pip install --requirement requirements.txt
CMD ["python", "server.py"]