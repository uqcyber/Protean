#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#          PROTEAN: LOKI           #
#                                  #
====================================

EOF
# == ++ == ++ == #
#     Setup      #
# == ++ == ++ == #

docker run -d -t \
    --name ti_loki \
    jwferreira/loki

docker cp $loki_filepath/. ti_loki:/protean_input


# == ++ == ++ == #
#   Execution    #
# == ++ == ++ == #   
docker exec \
    ti_loki \
    python ./Loki-0.32.1/loki.py -p protean_input -l ./loki_scan_log.csv --csv --dontwait --printall --noprocscan --intense

# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #   
printf 'copying results to collator ...\n'
docker cp ti_loki:/loki/src/results/. $(cd ../ && pwd)/protean/src/results/tool_outputs
printf 'exiting loki container...\n'
docker stop ti_loki
docker rm ti_loki
cat << "EOF"
====================================
#            Complete              #
====================================
EOF