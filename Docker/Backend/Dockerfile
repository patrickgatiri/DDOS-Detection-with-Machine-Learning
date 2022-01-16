FROM ubuntu:xenial

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.6 python3.6-dev python3-pip

WORKDIR /app
COPY requirements.txt .
RUN rm -f /usr/bin/python && ln -s /usr/bin/python3.6 /usr/bin/python
RUN rm -f /usr/bin/python3 && ln -s /usr/bin/python3.6 /usr/bin/python3

RUN pip3 install -U pip
RUN pip3 install -U setuptools
RUN pip3 install -r requirements.txt

RUN pip3 install gunicorn==19.9.0

ADD ./DDOS_Detection/ /app/DDOS_Detection/
ADD ./Docker/ /app/Docker/

RUN mkdir -p /app/DDOS_Detection/static
