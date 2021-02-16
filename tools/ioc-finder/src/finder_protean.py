#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
from ioc_finder import find_iocs
import os
import time
import json
import sys
import pdfplumber #pdf reader

def convert_pdf_txt(path):
    """
    Uses the pdfplumber library to extract text from a pdf
    """
    text = ""
    with pdfplumber.open(path) as pdf:
        for x in range(0, len(pdf.pages)):
            page = pdf.pages[x]
            extracted = page.extract_text()
            if(extracted != None):
                text += page.extract_text()
    return text

if __name__ == '__main__':
    """
    Uses ioc-finder to extract observables from pdfs in the /protean_input folder, recording elapsed time
    and the average time it takes ioc-finder to finish extrating a file.
    """

    process_start_time = time.time()
    input_path = '/protean_input'
    extracted_files = {}

    # ensure expected output folders exist
    for required_folder in ["/raw", "/lsv"]:
        if not os.path.isdir('/ioc-finder_vol/'+ required_folder):
            os.mkdir('/ioc-finder_vol/'+ required_folder)

    count = 0
    extract_avg_numerator = 0
    for filename in os.listdir(input_path):
        # Extract text from pdf
        filepath = os.path.join(input_path, filename)
        content = convert_pdf_txt(filepath)
        #TODO: add support for other file types

        # Extract Indicators of Compromise from text, recording time
        extract_start_time = time.time()
        iocs = find_iocs(content)
        extract_avg_numerator += time.time() - extract_start_time
        extracted_files[filename] = iocs

        # remove ioc types that we do not want (email_addresses_complete returns loose email matches)
        for x in ["email_addresses_complete"]:
            del extracted_files[filename][x]

        count += 1
            
    process_end_time = time.time()

    # add some meta info on process run time
    extracted_files["meta"] = {
        "tool": "ioc-finder",
        "files_examined": count,
        "elapsed_time": process_end_time - process_start_time,
        "average_time": extract_avg_numerator / count,
    }

    print("ioc-finder scanned {} files".format(count))

    # used by machinae / when desired output is line separated observables
    all_iocs = set()
    for filename in extracted_files:
        if filename == 'meta': continue
        for ioc_type in extracted_files[filename]:
            all_iocs.update(extracted_files[filename][ioc_type])

    # lsv export (used by machinae)
    lsv_path = "/ioc-finder_vol/lsv/"
    lsv_filename = "iocfinder_lsv.txt"
    with open(lsv_path + lsv_filename, 'w') as lsv:
        lsv.write('\n'.join(all_iocs))

    # json export
    results_path = "/ioc-finder_vol/raw/"
    results_filename = "ioc-finder_results.json"
    with open(results_path + results_filename, 'w') as fp:
        json.dump(extracted_files, fp)