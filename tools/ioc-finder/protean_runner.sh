#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#        PROTEAN: IOC-FINDER       #
#                                  #
====================================

EOF
# == ++ == ++ == #
#     Setup      #
# == ++ == ++ == #

printf "running iocextract on files in $extract_filepath \n"
docker run -d -t \
    --name ti_finder \
    -v ioc-finder_vol:/ioc-finder_vol: \
    jwferreira/ioc-finder

docker cp $extract_filepath/. ti_finder:/protean_input

# == ++ == ++ == #
#   Execution    #
# == ++ == ++ == #   
docker exec \
    ti_finder \
    python3 ./ioc-finder/src/finder_protean.py

# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #   
printf 'copying results to collator ...\n'
docker cp ti_finder:/ioc-finder_vol/raw/. $(cd ../ && pwd)/protean/src/results/tool_outputs
printf 'exiting ioc-finder container...\n'
docker stop ti_finder
docker rm ti_finder
cat << "EOF"
====================================
#            Complete              #
====================================
EOF