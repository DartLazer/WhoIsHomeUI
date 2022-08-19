ARG WHOIH_PORT
FROM python:3-slim-buster
ARG WHOIH_PORT
RUN apt update
RUN apt install -y cron curl
RUN echo "* * * * * curl -s http://0.0.0.0:${WHOIH_PORT}/scan/" | crontab -
CMD ["cron","-f"]