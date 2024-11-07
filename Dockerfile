# Build stage
FROM python:3.12-slim-bullseye AS builder

# Install dependencies only once
RUN apt-get update \
    && apt-get install -y --no-install-recommends procps gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code
COPY WhoIsHomeUIDjango /app

# Production stage
FROM python:3.12-slim-bullseye AS app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

# Copy installed packages and application code from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Install necessary packages including perl, arp-scan, and avahi-daemon
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gnupg2 net-tools arp-scan libcap2-bin perl libwww-perl avahi-daemon avahi-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update ieee-oui.txt using get-oui script
RUN cd /usr/share/arp-scan \
    && get-oui -v

# Copy the avahi service file to advertise whoishome.local with dynamic port
RUN echo '<?xml version="1.0" standalone="no"?>\n<!DOCTYPE service-group SYSTEM "avahi-service.dtd">\n<service-group>\n  <name replace-wildcards="yes">WhoIsHome</name>\n  <service>\n    <type>_http._tcp</type>\n    <port>${WHOIH_PORT}</port>\n  </service>\n</service-group>' > /etc/avahi/services/whoishome.service

# Enable avahi-daemon
RUN systemctl enable avahi-daemon

# Set working directory
WORKDIR /app