#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
import os
import json
import time

def collate_aiengine():
    """
    Imports and adds the results of aiengine into a global JSON view.
    """
    with open(input_filepath + "aiengine_results.json", 'r') as fp:
        aiengine_json = json.load(fp)
    return aiengine_json

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

def collate_loki():
    """
    Imports and adds the results of Loki into a global JSON view.
    """
    with open(input_filepath + "loki_results.json", 'r') as fp:
        loki_json = json.load(fp)
    return loki_json

def collate_iocextract():
    """
    Imports and adds the results of iocextract into a global JSON view.
    """
    with open(input_filepath + "iocextract_results.json", 'r') as fp:
        iocextract_json = json.load(fp)
    return iocextract_json

def collate_iocfinder():
    """
    Imports and adds the results of ioc-finder into a global JSON view.
    """
    with open(input_filepath + "ioc-finder_results.json", 'r') as fp:
        iocfinder_json = json.load(fp)
    return iocfinder_json

def collate_extractors():
    """
    Imports and adds the results of ioc-finder & iocextract into a global JSON view.
    As both tools are present, it flags the source of disjoint observables.
    """
    extract_collation = {}

    # open individual results
    with open(input_filepath + "ioc-finder_results.json", 'r') as fp1:
        iocfinder_json = json.load(fp1)
        
    with open(input_filepath + "iocextract_results.json", 'r') as fp2:
        iocextract_json = json.load(fp2)

    # collate results and mark differences
    for filename in iocfinder_json:
        if filename == "meta": continue
        if filename not in iocfinder_json:
            print("mismatch between parsed files")
            exit

        for ioc_type in iocfinder_json[filename]:
            if ioc_type not in extract_collation:
                extract_collation[ioc_type] = []

            # iocextract empty, add all iocfinder results
            if (ioc_type not in iocextract_json[filename]) or (len(iocextract_json[filename][ioc_type]) == 0):
                for val in iocfinder_json[filename][ioc_type]:
                    replacement = {
                        "value": val,
                        "source": "ioc-finder",
                    }
                    extract_collation[ioc_type].append(replacement)
                continue

            # ioc-finder empty, add all iocextract results
            if ioc_type not in iocfinder_json[filename] or len(iocfinder_json[filename][ioc_type]) == 0:
                for val in iocextract_json[filename][ioc_type]:
                    replacement = {
                        "value": val,
                        "source": "iocextract",
                    }
                    extract_collation[ioc_type].append(replacement)
                continue

            # == PERFORM SET OPERATIONS AND FLAG DIFFERENCES == #

            # flag iocs that only exist in iocfinder, and not in iocextract
            diff = set(iocfinder_json[filename][ioc_type]) - set(iocextract_json[filename][ioc_type])

            for val in diff:
                # remove and replace duplicate with formatted entry
                iocfinder_json[filename][ioc_type].remove(val)
                replacement = {
                    "value": val,
                    "source": "ioc-finder",
                }
                extract_collation[ioc_type].append(replacement)

            # flag iocs that only exist in iocextract, and not in iocfinder
            diff = set(iocextract_json[filename][ioc_type]) - set(iocfinder_json[filename][ioc_type])

            for val in diff:
                # remove and replace duplicate with formatted entry
                iocextract_json[filename][ioc_type].remove(val)
                replacement = {
                    "value": val,
                    "source": "iocextract",
                }
                extract_collation[ioc_type].append(replacement)
            
            # Add shared iocs
            intersection = set(iocfinder_json[filename][ioc_type]).intersection(set(iocextract_json[filename][ioc_type]))
            extract_collation[ioc_type].extend(intersection)

    return extract_collation


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

    # ensure expected output folders exist


    # if both extraction tools have been used, call a custom method that flags differences
    # otherwise if only one tool is present, add that tools results directly
    tools = {
        "iocextract": collate_iocextract,
        "ioc-finder": collate_iocfinder,
        "loki": collate_loki,
        "machinae": collate_machinae,
        "aiengine": collate_aiengine,
    }

    # check if both extract tools were used, using a different collation method if so
    if os.path.isfile(input_filepath + "iocextract_results.json") and os.path.isfile(input_filepath + "ioc-finder_results.json"):
        global_output["extracted_iocs"] = collate_extractors()
        global_output["meta"]["tools"].extend(["iocextract", "ioc-finder"])
        #remove the tools from the following check, as they have already been collated
        tools.pop("iocextract")
        tools.pop("ioc-finder")

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
