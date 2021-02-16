#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
printf '\n== Building: ioc-finder ==\n\n'
docker stop ti_finder
docker rm ti_finder
docker volume rm ioc-finder_vol
docker build -t jwferreira/ioc-finder:latest .
printf '\n== Finished Building ==\n'