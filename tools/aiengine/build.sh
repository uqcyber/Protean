#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
printf '\n== Building: AIEngine ==\n\n'
docker stop ti_aiengine
docker rm ti_aiengine
docker volume rm aiengine_vol
docker build -t jwferreira/aiengine:latest .
printf '\n== Finished Building ==\n'