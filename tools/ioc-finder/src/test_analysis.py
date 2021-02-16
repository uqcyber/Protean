#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
import os
import json
import time
import copy

def count_iocs(json_results):
    """
    Counts the number of occurences of a type of Indicator of Compromise (e.g. ipv4 address)
    """
    result = {}
    result["meta"] = json_results["meta"]
    result["iocs"] = {}
    result["iocs"]["total_iocs"] = 0
    # count number of parsed iocs
    for filename in json_results:
        if filename == "meta": continue
        for ioc in json_results[filename]:
            count = 0
            if ioc not in result["iocs"]:
                result["iocs"][ioc] = count

            # these types return dictionaries, so fix the count
            if ioc in ["attack_mitigations", "attack_tactics", "attack_techniques"]:
                for key in json_results[filename][ioc]:
                    count += len(set(json_results[filename][ioc][key]))
            else:
                count += len(set(json_results[filename][ioc]))

            result["iocs"][ioc] += count
            result["iocs"]["total_iocs"] += count
    return result


if __name__ == '__main__':
    """
    For all 'raw' results (directly from performance_test.py) found in the results directory,
    count the number of observables found and average metrics across test instances (identified by
    number of files extracted).
    """

    header = "iocfinder_raw_"
    trailer = "_XX-XX-XX.json"
    path = "/ioc-finder/src/results/raw"
    average_results = {}

    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'r') as fp:
            iocfinder_json = json.load(fp)
        # string splitting to get the file amount identifier (e.g. '5files')
        identifier = filename[len(header):len(filename)-len(trailer)]

        # basic format check
        if (len(iocfinder_json) == 0 or 'meta' not in iocfinder_json):
            exit("incorrect json format")

        # first time seeing this identifier, setup object and count observables
        if identifier not in average_results:
            file_results = count_iocs(iocfinder_json)
            files = list(iocfinder_json.keys())
            files.remove("meta")

            average_results[identifier] = {
                "tool": file_results['meta']['tool'],
                "files_examined": file_results['meta']['files_examined'],
                "files": files,
                "elapsed_times": [],
                "avg_extract_times": [],
                "throughputs": [],
                "avg_elapsed_time": 0,
                "avg_avg_extract_time": 0,
                "avg_throughput": 0,
                "iocs": file_results["iocs"]
            }

        # Append & average results
        average_results[identifier]["elapsed_times"].append(iocfinder_json["meta"]["elapsed_time"])
        average_results[identifier]["avg_extract_times"].append(iocfinder_json["meta"]["average_time"])
        average_results[identifier]["throughputs"].append(average_results[identifier]["iocs"]["total_iocs"] / iocfinder_json["meta"]["elapsed_time"])
        average_results[identifier]["avg_elapsed_time"] = sum(average_results[identifier]["elapsed_times"]) / len(average_results[identifier]["elapsed_times"])
        average_results[identifier]["avg_avg_extract_time"] =  sum(average_results[identifier]["avg_extract_times"]) / len(average_results[identifier]["avg_extract_times"])
        average_results[identifier]["avg_throughput"] = sum(average_results[identifier]["throughputs"]) /  len(average_results[identifier]["throughputs"])
    
    # json export
    results_filepath = "/ioc-finder/src/results/processed/"
    results_filename = "finder_processed_{}.json".format(time.strftime('%H-%M-%S', time.localtime()))
    with open(results_filepath + results_filename, 'w') as fp:
        json.dump(average_results, fp)
