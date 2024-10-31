# Here is the build image
FROM python:3.12-slim-bullseye as builder
RUN apt-get update \
    && apt-get install procps gcc -y \
    && apt-get clean
COPY requirements.txt /app/requirements.txt
WORKDIR app
RUN pip install --user -r requirements.txt
COPY WhoIsHomeUIDjango /app

# Here is the production image
FROM python:3.12-slim-bullseye as app
ENV PYTHONUNBUFFERED=1
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
RUN apt update \
    && apt install -y net-tools arp-scan libcap2-bin curl \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*
# Download the latest vendor files for arp-scan so it can resolve MAC addresses to vendor names
RUN curl -o /usr/share/arp-scan/ieee-oui.txt https://standards-oui.ieee.org/oui/oui.txt

WORKDIR app
ENV PATH=/root/.local/bin:$PATH