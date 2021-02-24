#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
printf '\n== Building: Loki ==\n\n'
docker stop ti_loki
docker rm ti_loki
docker volume rm loki_vol
docker build -t jwferreira/loki:latest .
printf '\n== Finished Building ==\n'