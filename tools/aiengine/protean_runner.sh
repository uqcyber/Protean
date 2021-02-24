#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#        PROTEAN: AIENGINE         #
#                                  #
====================================

EOF
# == ++ == ++ == #
#     Setup      #
# == ++ == ++ == #
printf "AIEngine: Path = $aiengine_filepath\n"

docker run -d -t \
    --name ti_aiengine \
    -v aiengine_vol:/aiengine_vol: \
    jwferreira/aiengine

docker cp $aiengine_filepath/. ti_aiengine:/pcap

# == ++ == ++ == #
#   Execution    #
# == ++ == ++ == #   
docker exec \
    ti_aiengine \
    python ./aiengine/src/aiengine_fileadapter.py

# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #   
printf 'copying results to collator ...\n'
docker cp ti_aiengine:/aiengine_vol/. $(cd ../ && pwd)/protean/src/results/tool_outputs
printf 'exiting aiengine container...\n'
docker stop ti_aiengine
docker rm ti_aiengine
cat << "EOF"
====================================
#            Complete              #
====================================
EOF