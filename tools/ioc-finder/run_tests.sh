#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#      IOC-FINDER TEST RUNNER      #
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
    --name ti_finder \
    jwferreira/ioc-finder

# == ++ == ++ == #
#   Unit Tests   #
# == ++ == ++ == #   
if [ "$unit" == y ]
then
    printf 'running unit tests...\n'
    docker exec -d\
        ti_finder \
        python3 ./ioc-finder/src/unit_tests.py
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
            ti_finder \
            python3 ./ioc-finder/src/performance_tests.py $i $repetitions
    done
    
    if [ "$analysis" == y ]
    then
        printf 'analysing results...\n'
        docker exec \
            ti_finder \
            python3 ./ioc-finder/src/test_analysis.py
    fi

    if [ "$copy" == y ]
    then
        printf 'copying results to host machine ...\n'
        docker cp ti_finder:/ioc-finder/src/results $(pwd)/src/
    fi
fi

# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #   
printf 'exiting ioc-finder container...\n'
docker stop ti_finder
docker rm ti_finder
cat << "EOF"
====================================
#            Complete              #
====================================
EOF