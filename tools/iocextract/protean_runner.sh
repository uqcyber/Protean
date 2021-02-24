#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#        PROTEAN: IOCEXTRACT       #
#                                  #
====================================

EOF
# == ++ == ++ == #
#     Setup      #
# == ++ == ++ == #

printf "running iocextract on files in $extract_filepath \n"
docker run -d -t \
    --name ti_extract \
    -v iocextract_vol:/iocextract_vol: \
    jwferreira/iocextract

docker cp $extract_filepath/. ti_extract:/protean_input

# == ++ == ++ == #
#   Execution    #
# == ++ == ++ == #   
docker exec \
    ti_extract \
    python3 ./iocextract/src/extract_protean.py

# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #   
printf 'copying results to collator ...\n'
docker cp ti_extract:/iocextract_vol/raw/. $(cd ../ && pwd)/protean/src/results/tool_outputs
printf 'exiting iocextract container...\n'
docker stop ti_extract
docker rm ti_extract
cat << "EOF"
====================================
#            Complete              #
====================================
EOF