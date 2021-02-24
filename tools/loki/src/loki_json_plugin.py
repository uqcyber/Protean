#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
import os
import json
import csv
import time
from parse import parse
import re

def ExportJSON():
    """
    Plugin for the Loki tool which exports scan results in JSON format at the end of a scan.
    For this plugin to work, Loki must be run with the following commands:

        -l ./loki_scan_log.csv --csv

    As Loki does not provide the architecture to custom log data during a scan's execution,
    this plugin works by having Loki export its scans to a file (to a known path and filename)
    and then proceeds to convert the csv logs into a new JSON format.
    """
    print("\n\n======== json plugin\n")

    # log file location
    log_path = "/"
    log_filename = "loki_scan_log.csv"

    # ensure expected output folders exist
    results_path = "/loki/src/results/"
    if not os.path.isdir(results_path):
        os.mkdir(results_path)

    # csv line format: TIMESTAMP, HOSTNAME, MESSAGE_TYPE, MODULE, MESSAGE
    TIMESTAMP = 0
    MESSAGE_TYPE = 2 # = {INFO, WARNING, ALERT}
    MODULE = 3 # = {FileScan, ProcessScan}
    MESSAGE = 4 # = Scanning $path TYPE: %s SIZE: %d

    json_output = {
        "info": {},
        "alerts": {},
        "warnings": {}
    }

    with open(log_path + log_filename, 'r') as fp:
        csv_reader = csv.reader(fp, delimiter=',')
        timestamp = 0
        for row in csv_reader:

            # Get the scan's timestamp (used for start/end time)
            timestamp = row[TIMESTAMP]

            if row[MODULE] == "FileScan":

                if row[MESSAGE_TYPE] == 'INFO':
                    details = parse('Scanning {location} TYPE: {filetype} SIZE: {size}', row[MESSAGE])
                    
                    # skip messages that don't have the right format
                    if details == None:
                        continue

                    # If meta info hasn't been initialised yet (first scan)
                    if "meta" not in json_output:
                        json_output["meta"] = {}
                        json_output["meta"]["total_files_scanned"] = 0
                        json_output["meta"]["total_bytes"] = 0
                        json_output["meta"]["total_warnings"] = 0
                        json_output["meta"]["total_alerts"] = 0
                        json_output["meta"]["start_time"] = timestamp
                        json_output["meta"]["scan_path"] = details['location']
                        
                    # First time seeing this type
                    if details['filetype'] not in json_output['info']:
                        json_output['info'][details['filetype']] = {
                            "total_type_scanned" : 0,
                            "cumulative_bytes": 0
                        }

                    # Increment values
                    json_output['info'][details['filetype']]["total_type_scanned"] += 1
                    json_output['info'][details['filetype']]["cumulative_bytes"] += int(details['size'])
                    json_output['meta']["total_files_scanned"] += 1
                    json_output['meta']["total_bytes"] += int(details['size'])

                elif row[MESSAGE_TYPE] in ['WARNING', 'ALERT']:
                    scan_type = row[MESSAGE_TYPE].lower() + "s"
                    details = parse('FILE: {file} SCORE: {score} TYPE: {filetype} SIZE: {size} FIRST_BYTES: {first_bytes} MD5: {md5} SHA1: {sha1} SHA256: {sha256} CREATED: {created} MODIFIED: {modified} ACCESSED: {accessed} REASON_1: {remainder}', row[MESSAGE])

                    # skip messages that don't have the right format
                    if details == None:
                        print("skipping {}".format(row[MESSAGE]))
                        continue

                    json_output[scan_type][details['file']] = {
                        'warning_meta': {
                            "created": details['created'],
                            "modified": details['modified'],
                            "accessed": details['accessed'],
                            "filetype": details['filetype'],
                            "size": details['size']
                        },
                        "score": details['score'],
                        "first_bytes": details['first_bytes'],
                        'hashes': {
                            "md5": details['md5'],
                            "sha1": details['sha1'],
                            "sha256": details['sha256']
                        },
                        'reasons': []
                    }

                    # This is a bit hacky, but I add REASON_1 back in after it was stripped by the above parse method
                    # then prepend REASON back into the string after the regex split as it allows for the following 
                    # string-split and search-loop to be cleaner.
                    #   
                    # The string-split regex matches all REASONS within the string and splits them.
                    # The 0th index is removed because remainder is guaranteed to start with "REASON_1" and
                    # re.split() will include an string for anything occuring before the first match (in this case, nothing)
                    remainder = "REASON_1: " + details['remainder']
                    reasons = re.split('REASON_\d+:', remainder)
                    reasons.pop(0) 
                    for i in range(0, len(reasons)):
                        reasons[i] = 'REASON:' + reasons[i]

                    # Each entry in reasons[] is a string beginning with "REASON:", followed by <k,v> pairs
                    # in the format <"$KEY:", value>. For each of a REASON's keys, the loop creates
                    # and populates a dictionary for it in the following format.
                    #
                    # "reasons": [
                    #     {
                    #         "reason": "Malware Hash",
                    #         "type": "MD5",
                    #         "hash": "8979594423b68489024447474d113894",
                    #         "subscore": "100"
                    #     }]
                    #
                    # note: the following is required as the format of Loki logs past 'REASON' is often missing spacing
                    # between reasons and the order/existence of the keys is not guaranteed.
                    current_reason = {}
                    potential_keys = ["REASON", "MATCH", "TYPE", "DESCRIPTION", "HASH", "SUBSCORE", "DESC", "REF", "MATCHES"]
                    for reason in reasons:
                        for k in potential_keys:
                            search_regex = '(?<=' + k + ': )(.*?)(?= [A-Z]+_?\d*:)'
                            reason_entry = re.search(search_regex, reason)
                            # if we matched a key value (e.g. SUBSCORE: 42)
                            if reason_entry:
                                # REASONS & their key values are what we are trying to insert as an object
                                if k == "REASON":
                                    if 'reason' not in current_reason: # first match on reason
                                        current_reason['reason'] = reason_entry.group()
                                    else: #another reason exists, add the previous one and create this one
                                        json_output[scan_type][details['file']]['reasons'].append(current_reason)
                                        current_reason = {
                                            'reason': reason_entry.group()
                                        }
                                else:
                                    current_reason[k.lower()] = reason_entry.group()

                    # add the currently parsed reason
                    json_output[scan_type][details['file']]['reasons'].append(current_reason)

                    # increment meta counter
                    json_output['meta']["total_" + scan_type] += 1 

        # add in last-seen timestamp
        json_output["meta"]["end_time"] = timestamp

        print("Processed {} files, {} warnings and {} alerts".format(
            json_output["meta"]["total_files_scanned"],
            json_output["meta"]["total_warnings"],
            json_output["meta"]["total_alerts"],
            ))

        # json export
        results_filename = "loki_results.json"

        # results_filename = "loki_{}_{}.json".format(json_output["meta"]["scan_path"], 
        #     time.strftime('%H-%M-%S', time.localtime()))

        with open(results_path + results_filename, 'w') as fp:
            json.dump(json_output, fp)
        print("\n======== json plugin complete\n")
        
# Register the plugin to execute at Phase 2 (After Scans)
LokiRegisterPlugin("PluginJSON", ExportJSON, 2)