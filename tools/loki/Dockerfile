#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
# Dockerfile for the 'Loki' tool
FROM ubuntu:18.04
ENV LANG C.UTF-8

# install packages
RUN apt-get update -y && apt-get install -y \
    python2.7 \
    python-pip \
    libssl-dev \
    curl

# install pip requirements
COPY /config /loki/config
RUN pip2 install -r /loki/config/requirements.txt

# download & install open licensed windows binaries (via google-filament)
RUN curl -L >filament.tgz https://github.com/google/filament/releases/download/v1.9.9/filament-v1.9.9-windows.tgz \
    && tar -xzvf filament.tgz --one-top-level    
    
# loki setup
RUN curl -L >loki.tar.gz https://github.com/Neo23x0/Loki/archive/0.32.1.tar.gz \
    && tar -xzvf loki.tar.gz \
    && cd Loki-0.32.1 \
    && python loki-upgrader.py

# copy across /src
COPY /src /loki/src

# move the json plugin & excludes configuration files to the right places
RUN cp /loki/src/loki_json_plugin.py /Loki-0.32.1/plugins/loki-plugin-json.py \
    && cp /loki/config/excludes.cfg /Loki-0.32.1/config/excludes.cfg
