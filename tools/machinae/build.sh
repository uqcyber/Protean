#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
printf '\n== Building: Machinae ==\n\n'
docker stop ti_machinae
docker rm ti_machinae
docker volume rm machinae_vol
docker build -t jwferreira/machinae:latest .
printf '\n== Finished Building ==\n'