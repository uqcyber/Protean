#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
printf '\n== Building: iocextract ==\n\n'
docker stop ti_extract
docker rm ti_extract
docker volume rm iocextract_vol
docker build -t jwferreira/iocextract:latest .
printf '\n== Finished Building ==\n'