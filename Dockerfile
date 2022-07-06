FROM python:3.9.0

LABEL maintainer=victomartin@gmail.com

COPY *.py /usr/src
COPY *.sh /usr/src

RUN mkdir /usr/src/speedtest && \
    apt update &&  \
    apt install -y \
        pigz \
        speedtest-cli \
        tar

WORKDIR /usr/src
