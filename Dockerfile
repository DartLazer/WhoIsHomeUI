FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /mysite
WORKDIR /mysite
COPY mysite /mysite/
COPY requirements.txt /mysite/
RUN  pip install -r requirements.txt && apt update && apt install -y \ 
    net-tools \
    arp-scan 
