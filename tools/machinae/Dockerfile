#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
# Dockerfile for the 'machinae' tool
FROM ubuntu:18.04
ENV LANG C.UTF-8

# install packages
RUN apt-get update -y && apt-get install -y \
    python3-pip \
    python3-dev

# install pip requirements & Machinae configuration file
COPY /config /machinae/config
COPY /src /machinae/src

RUN pip3 install -r /machinae/config/requirements.txt \
    && mv /machinae/config/machinae.yml /etc/machinae.yml \
    && mkdir /machinae/src/results