#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#      MACHINAE TEST RUNNER        #
#                                  #
====================================

EOF

# == ++ == ++ == #
#   Test Setup   #
# == ++ == ++ == #
printf 'Run unit tests? [y\\n]: '
read unit
printf 'Copy files to host machine? [y\\n]: '
read copy

RESULTS_DIR="src/results"
if [ -d "$RESULTS_DIR" ]
then
    printf 'src/results directory found :)\n'
else
    printf 'src/results directory not found on host machine, creating...\n'
    mkdir src/results
fi

# == ++ == ++ == #
#      Tests     #
# == ++ == ++ == #  
printf "running machinae test...\n"
docker run -d -t\
    --name ti_machinae \
    jwferreira/machinae

# == ++ == ++ == #
#   Unit Tests   #
# == ++ == ++ == #   
if [ "$unit" == y ]
then
    printf 'Running unit tests...'
    docker exec \
        ti_machinae \
        python3 ./machinae/src/unit_tests.py
fi

# Machinae sites that work (confirmed by unit tests)
sites="-s ipwhois,sans,fortinet_classify,vt_ip\
,vt_domain,vt_url,vt_hash,vxvault,stopforumspam\
,cymru_mhr,threatcrowd_ip_report,macvendors"

for otype in "ipv4" "fqdn" "email" "hash" "url"
do
    input="-i ./machinae/src/test_inputs/input-$otype.txt"
    output="-oJ -f ./machinae/src/results/machinae-results-$otype.json"
    printf "Testing Machinae Observable: $otype\n"
    docker exec \
        ti_machinae \
        machinae $output $input $sites
done

if [ "$copy" == y ]
then
    printf 'copying results to host machine ...\n\n'
    docker cp ti_machinae:/machinae/src/results/. $(pwd)/src/results
fi

# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #   
printf 'exiting machinae container...\n'
docker stop ti_machinae
docker rm ti_machinae
cat << "EOF"
====================================
#            Complete              #
====================================
EOF