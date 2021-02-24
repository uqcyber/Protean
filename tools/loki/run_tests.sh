#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#         LOKI TEST RUNNER         #
#                                  #
====================================

EOF

# == ++ == ++ == #
#   Test Setup   #
# == ++ == ++ == #
printf 'Path to scan (a = bin, b = system, c = windows): '
read path
if [ "$path" == "a" ]
then
    printf 'scan directory /bin \n'
    path='bin'
elif [ "$path" == "b" ]
then
    printf 'scanning entire system\n'
    path='./'
else
    printf 'scanning windows binaries\n'
    path='filament'
fi

# == ++ == ++ == #
#   Perf. Tests  #
# == ++ == ++ == #  
docker run -d -t \
    --name ti_loki \
    jwferreira/loki

printf "running performance test 5 times...\n"

for i in {1..5}
do
    docker exec \
        ti_loki \
        python ./Loki-0.32.1/loki.py -p $path -l ./loki_scan_log.csv --csv --dontwait --printall --noprocscan --intense
done

printf 'copying results to loki/results ...\n'
docker cp ti_loki:/loki/src/results $(pwd)/src/

# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #   
printf 'exiting loki container...\n'
docker stop ti_loki
docker rm ti_loki
cat << "EOF"
====================================
#            Complete              #
====================================
EOF