#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
import os
import json
import time


def collate_machinae():
    """
    Imports and adds the results of Machinae into a global JSON view.
    As Machinae returns line-separated JSON, each line must be individually parsed.
    This also skips adding empty / error results
    """
    machinae_collation = []
    with open(input_filepath + "machinae_results.json", 'r') as fp:
        for line in fp:
            json_line = json.loads(line)
            if json_line['results']:
                if "error_info" in json_line['results']: continue
                machinae_collation.append(json_line)    
    return machinae_collation

def collate_iocfinder():
    """
    Imports and adds the results of ioc-finder into a global JSON view.
    """
    with open(input_filepath + "ioc-finder_results.json", 'r') as fp:
        iocfinder_json = json.load(fp)
    return iocfinder_json

if __name__ == '__main__':
    """
    This program reads the output file of each tool within the Protean pipeline and collates it into a single
    global JSON file. If two tools with the same output are used (iocextract & ioc-finder), a different parse method is used.
    """

    # dictionary to store the global collated output
    global_output = {
        "meta": {
            "tools": []
        },
    }

    input_filepath = os.path.dirname(__file__) + "/results/tool_outputs/"
    if not os.path.isdir(input_filepath) or len(os.listdir(input_filepath)) == 0:
        print("Tool outputs are not found. Please run Protean first.")
        exit()

    # if both extraction tools have been used, call a custom method that flags differences
    # otherwise if only one tool is present, add that tools results directly
    tools = {
        "ioc-finder": collate_iocfinder,
        "machinae": collate_machinae,
    }

    for name in tools:
        tool_output_file = "{}_results.json".format(name)
        if os.path.isfile(input_filepath + tool_output_file):
            global_output[name] = tools[name]()
            global_output["meta"]["tools"].append(name) 

    # json export
    results_filepath =  os.path.dirname(__file__) + "/results/"
    results_filename = "global_collation.json"
    with open(results_filepath + results_filename, 'w') as fp:
        json.dump(global_output, fp)
