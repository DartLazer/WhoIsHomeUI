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
RUN apt-get update \
    && apt-get install -y --no-install-recommends gnupg2 net-tools arp-scan libcap2-bin curl \
    && curl -fsSL https://ftp-master.debian.org/keys/archive-key-11.asc | gpg --dearmor -o /usr/share/keyrings/debian-archive-keyring.gpg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Download the latest vendor files for arp-scan so it can resolve MAC addresses to vendor names
RUN curl -o /usr/share/arp-scan/ieee-oui.txt https://standards-oui.ieee.org/oui/oui.txt

WORKDIR app
ENV PATH=/root/.local/bin:$PATH