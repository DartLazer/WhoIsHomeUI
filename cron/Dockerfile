ARG WHOIH_PORT
FROM alpine:latest
ARG WHOIH_PORT
RUN apk --no-cache add curl
RUN echo "* * * * * curl http://localhost:${WHOIH_PORT}/scan/" | crontab -
CMD ["crond","-f"]