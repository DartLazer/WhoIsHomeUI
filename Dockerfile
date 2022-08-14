FROM python:3-buster
ENV PYTHONUNBUFFERED=1
RUN mkdir /mysite
WORKDIR /mysite
COPY mysite /mysite/
COPY requirements.txt /mysite/
RUN pip install -r requirements.txt 
RUN apt update 
RUN apt install -y net-tools arp-scan