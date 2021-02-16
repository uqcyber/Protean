#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
from ioc_finder import find_iocs
import os
import copy
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
    Uses pdfs in the APTNotes repository to test the ioc-finder library, recording elapsed time
    and the average time it takes ioc-finder to finish extrating a file.

    Program arguments:
        - argv[1] maximum: sets the maximum amount of files to attempt extraction of
        - argv[2] repetitions: repeat the test instance this amount of times
    """
    process_start_time = time.time()
    apt_notes_path = '/APTNotes'
    extracted_files = {}

    # ensure expected output folders exist
    for required_folder in ["/results", "/results/raw", "/results/processed", "/results/lsv"]:
        if not os.path.isdir('/ioc-finder/src'+ required_folder):
            os.mkdir('/ioc-finder/src'+ required_folder)

    # Deal with program inputs: max files to read, test repetitions
    maximum = 1
    repetitions = 1
    if len(sys.argv) -1 == 2:
        maximum = int(sys.argv[1])
        repetitions = int(sys.argv[2])
        if(maximum < 1 or not isinstance(maximum, int)):
            exit("max argument out of bounds [1, inf]")
        if(repetitions < 1 or not isinstance(repetitions, int)):
            exit("repetition argument out of bounds [1, inf]")

    # Conduct the test $repetitions times
    for i in range(0, repetitions):
        print("-> ioc-finder test instance {} ".format(i))
        count = 0
        extract_avg_numerator = 0
        # files that for whatever reason cause iocextract to hang, likely to do with pdf plumber
        skip_files = ["Elephantosis.pdf", "butterfly-corporate-spies-out-for-financial-gain.pdf"]

        for filename in os.listdir(apt_notes_path):
            if(count > maximum - 1):
                break
            if(filename in skip_files):
                continue

            # Extract text from pdf
            filepath = os.path.join(apt_notes_path, filename)
            content = convert_pdf_txt(filepath)

            # Extract Indicators of Compromise from text, recording time
            extract_start_time = time.time()
            iocs = find_iocs(content)
            extract_avg_numerator += time.time() - extract_start_time
            extracted_files[filename] = iocs

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
        lsv_path = "/ioc-finder/src/results/lsv/"
        lsv_filename = "iocfinder_lsv.txt"
        with open(lsv_path + lsv_filename, 'w') as lsv:
            lsv.write('\n'.join(all_iocs))

        # json export
        results_path = "/ioc-finder/src/results/raw/"
        results_filename = "iocfinder_raw_{}_files_{}.json".format(count, 
            time.strftime('%H-%M-%S', time.localtime()))
        with open(results_path + results_filename, 'w') as fp:
            json.dump(extracted_files, fp)