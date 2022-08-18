FROM python:3-slim-buster
ENV PYTHONUNBUFFERED=1
RUN mkdir /mysite
WORKDIR /mysite
COPY mysite /mysite/
COPY requirements.txt /mysite/
RUN apt update && apt install -y net-tools arp-scan procps gcc
RUN  pip install -r requirements.txt

