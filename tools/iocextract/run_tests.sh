#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#      IOCEXTRACT TEST RUNNER      #
#                                  #
====================================

EOF

# == ++ == ++ == #
#   Test Setup   #
# == ++ == ++ == #
printf 'Run unit tests? [y\\n]: '
read unit
printf 'Run performance tests? [y\\n]: '
read performance
if [ "$unit" == "n" ] && [ "$performance" == "n" ]
then
    printf 'No tests requested, exiting...'
    exit 0
fi

if [ "$performance" == "y" ]
then
    printf 'Please enter amount of test repetitions: '
    read repetitions
    printf 'Analyse results? [y\\n]: '
    read analysis
    printf 'Copy files to host machine? [y\\n]: '
    read copy
fi

docker run -d -t \
    --name ti_extract \
    jwferreira/iocextract

# == ++ == ++ == #
#   Unit Tests   #
# == ++ == ++ == #  
if [ "$unit" == y ]
then
    printf 'running unit tests...'
    docker exec \
        ti_extract \
        python3 ./iocextract/src/unit_tests.py
fi

# == ++ == ++ == #
#   Perf. Tests  #
# == ++ == ++ == #   
if [ "$performance" == y ]
then
    printf "running performance test $repetitions times\n"
    for i in 1 5 10 15 20 25
    do
        docker exec \
            ti_extract \
            python3 ./iocextract/src/performance_tests.py $i $repetitions
    done

    if [ "$analysis" == y ]
    then
        printf 'analysing results...\n'
        docker exec \
            ti_extract \
            python3 ./iocextract/src/test_analysis.py
    fi

    if [ "$copy" == y ]
    then
        printf 'copying results to host machine ...\n'
        docker cp ti_extract:/iocextract/src/results $(pwd)/src/
    fi
fi

# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #  
printf 'exiting iocextract container...\n'
docker stop ti_extract
docker rm ti_extract
cat << "EOF"
====================================
#            Complete              #
====================================
EOF