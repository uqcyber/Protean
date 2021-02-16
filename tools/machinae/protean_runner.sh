#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
cat << "EOF"

====================================
#                                  #
#        PROTEAN: MACHINAE         #
#                                  #
====================================

EOF
# == ++ == ++ == #
#     Setup      #
# == ++ == ++ == #

# Machinae can either use input from {ioc-finder, custom_filepath}
if [ "$machinae_data_src" == "ioc-finder" ]
then
    printf "Machinae Data Source: $machinae_data_src\n"
    optional_input_vol="-v ${machinae_data_src}_vol:/machinae_input"
    input_filename="${machinae_data_src}_lsv.txt"
    input="-i ./machinae_input/lsv/$input_filename"
fi

docker run -d -t\
    --name ti_machinae \
    $optional_input_vol \
    -v machinae_vol:/results: \
    jwferreira/machinae

if [ "$machinae_data_src" != "ioc-finder" ]
then
    printf 'Machinae Data Source: custom file path\n'
    input_filepath="$(dirname $machinae_data_src)"
    input_filename="$(basename $machinae_data_src)"
    input="-i ./machinae_input/$input_filename"
    docker cp $input_filepath/. ti_machinae:/machinae_input
    printf "Path = $input_filepath | Filename = $input_filename\n"
fi
# == ++ == ++ == #
#   Execution    #
# == ++ == ++ == #   

output="-oJ -f ./results/machinae_results.json"
# Machinae sites that work (confirmed by unit tests)
sites="-s ipwhois,sans,fortinet_classify,vt_ip\
,vt_domain,vt_url,vt_hash,vxvault,stopforumspam\
,cymru_mhr,threatcrowd_ip_report,macvendors"

docker exec \
    ti_machinae \
    machinae $input $output $sites
    
# == ++ == ++ == #
#    Clean-up    #
# == ++ == ++ == #   
printf 'copying results to collator ...\n'
docker cp ti_machinae:/results/. $(cd ../ && pwd)/protean/src/results/tool_outputs
printf 'exiting machinae container...\n'
docker stop ti_machinae
docker rm ti_machinae
cat << "EOF"
====================================
#            Complete              #
====================================
EOF