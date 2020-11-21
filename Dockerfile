FROM python:3.9.0

LABEL maintainer=victomartin@gmail.com

COPY *.py /usr/src

RUN apt update &&  \
    apt install -y pigz tar

WORKDIR /usr/src
