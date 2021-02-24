#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
# Dockerfile for the 'AIEngine' tool

FROM ubuntu:18.04
ENV LANG C.UTF-8

# install packages
RUN apt-get update -y && apt-get install -y \
    python2.7 \
    python-pip \
    libpcap-dev \
    libpcre3-dev \
    libboost1.65-all-dev \
    autoconf \
    automake \
    libtool \
    curl \
    wget

# aiengine set up
RUN curl -L >aiengine.tar.gz https://bitbucket.org/camp0/aiengine/downloads/aiengine-1.9.0.tar.gz \
    && tar -xzvf aiengine.tar.gz \
    && cd aiengine-1.9.0 \
    && ./autogen.sh \
    && ./configure --with-boost-libdir=/usr/lib/x86_64-linux-gnu \
    && make \
    && make install \
    && cd src \
    && make python

# download testing data, unzip & give nicer names
RUN wget -P /pcap -r -nH --cut-dirs=4 --no-parent --reject="index.html*" https://archive.ics.uci.edu/ml/machine-learning-databases/00516/arp_mitm/ARP%20MitM_pcap.pcapng.gz \
    && wget -P /pcap -r -nH --cut-dirs=4 --no-parent --reject="index.html*" https://archive.ics.uci.edu/ml/machine-learning-databases/00516/mirai/Mirai_pcap.pcap.gz \
    && wget -P /pcap -r -nH --cut-dirs=4 --no-parent --reject="index.html*" https://archive.ics.uci.edu/ml/machine-learning-databases/00516/ssdp_flood/SSDP%20Flood_pcap.pcap.gz \
    && gunzip /pcap/'ARP MitM_pcap.pcapng.gz' \
    && gunzip /pcap/Mirai_pcap.pcap.gz \
    && gunzip /pcap/'SSDP Flood_pcap.pcap.gz' \
    && mv /pcap/'ARP MitM_pcap.pcapng' /pcap/arp_mitm.pcapng \
    && mv /pcap/Mirai_pcap.pcap /pcap/mirai.pcap \
    && mv /pcap/'SSDP Flood_pcap.pcap' /pcap/ssdp_flood.pcap

# copy across testing file
COPY /src /aiengine/src