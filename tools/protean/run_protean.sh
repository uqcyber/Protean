#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
# Operates the Protean pipeline between tools
cat << "EOF"

    ____             __                 
   / __ \_________  / /____  ____ _____ 
  / /_/ / ___/ __ \/ __/ _ \/ __ `/ __ \
 / ____/ /  / /_/ / /_/  __/ /_/ / / / /
/_/   /_/   \____/\__/\___/\__,_/_/ /_/  LITE

EOF
# == ++ == ++ == #
#     Setup      #
# == ++ == ++ == #
RESULTS_DIR="src/results"
if [ -d "$RESULTS_DIR" ]
then
    printf 'src/results directory found :)\n'
else
    printf 'src/results directory not found on host machine, creating...\n'
    mkdir src/results
fi

COLLATABLES_DIR="src/results/tool_outputs"
if [ -d "$COLLATABLES_DIR" ]
then
    printf 'src/results/tool_outputs directory found :)\n'
else
    printf 'src/results/tool_outputs directory not found on host machine, creating...\n'
    mkdir src/results/tool_outputs
    mkdir src/results/api_outputs
fi

# Tool Selection
printf 'Use Saved Configuration [y\\n]: '
read config # used to speed up development, enter reused paths below
if [ "$config" = "y" ]
then
    extract_dir="C:\\Users\\james\\Documents\\pdfs"
    machinae_input="C:\\Users\\james\\Documents\\lsv\\test_lsv.txt"
    iocfinder_enabled="y"
    machinae_enabled="y"
else
    printf 'Enable all tools? [y\\n]: '
    read all_enabled
    if [ "$all_enabled" == "y" ]
    then
        iocfinder_enabled="y"
        machinae_enabled="y"
    else
        printf 'Enable ioc-finder? [y\\n]: '
        read iocfinder_enabled
        printf 'Enable Machinae? [y\\n]: '
        read machinae_enabled
    fi

    # extract set-up
    if [ "$iocfinder_enabled" == "y" ]
    then
        printf 'Please enter full path to desired Extract scan directory (e.g. C://Documents): '
        read extract_dir
    fi

    # machinae set-up
    if [ "$machinae_enabled" == "y" ]
    then
        printf 'Machinae Input: [ioc-finder, $custom_path]: '
        read machinae_input

        if [ "$machinae_input" == "ioc-finder" ] && [ "$iocfinder_enabled" != "y" ]
        then
            printf 'ioc-finder is not enabled, disabling Machinae\n'
            machinae_enabled="n"
        fi
    fi

fi

# all variables in this segment are exported
set -a
extract_filepath=$extract_dir
machinae_data_src=$machinae_input
set +a

# =================
#    EXTRACTORS
# =================
if [ "$iocfinder_enabled" == "y" ]
then
    (cd ../ioc-finder; ./build.sh; ./protean_runner.sh)
fi

# # =================
# #     MACHINAE
# # =================

if [ "$machinae_enabled" == "y" ]
then
    (cd ../machinae; ./build.sh; ./protean_runner.sh)
fi

# =================
#     COLLATE
# =================
printf '[Protean] collating outputs...\n'
python src/collator.py
printf '[Protean] polling apis...\n'
python src/api_dispatcher.py
printf '[Protean] Complete'
