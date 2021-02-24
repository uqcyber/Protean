#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
# Dockerfile for the 'iocextract' tool
FROM ubuntu:18.04
ENV LANG C.UTF-8

# install packages
RUN apt-get update -y && apt-get install -y \
    python3-pip \
    python3-dev \
    subversion

# install pip requirements
COPY /config /iocextract/config
RUN pip3 install -r /iocextract/config/requirements.txt

# download testing data
RUN svn export https://github.com/kbandla/APTnotes/trunk/2015 /APTNotes

# copy across files
COPY /src /iocextract/src