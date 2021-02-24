#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#       AIENGINE TEST RUNNER       #
#                                  #
====================================

EOF

# == ++ == ++ == #
#     Setup      #
# == ++ == ++ == #
docker run -d -t \
    --name ti_aiengine \
    jwferreira/aiengine

# == ++ == ++ == #
#   pcap tests   #
# == ++ == ++ == #   
docker exec \
    ti_aiengine \
    python ./aiengine/src/aiengine_fileadapter.py

printf 'copying results to host machine ...\n'
docker cp ti_aiengine:/aiengine/src/results $(pwd)/src/

# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #  
printf 'exiting aiengine container...\n'
docker stop ti_aiengine
docker rm ti_aiengine
cat << "EOF"
====================================
#            Complete              #
====================================
EOF