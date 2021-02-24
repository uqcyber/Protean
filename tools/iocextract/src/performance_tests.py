#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
import iocextract  # regex-based
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
    Uses pdfs in the APTNotes repository to test the iocextract library, recording elapsed time
    and the average time it takes iocextract to finish extrating a file.

    Program arguments:
        - argv[1] maximum: sets the maximum amount of files to attempt extraction of
        - argv[2] repetitions: repeat the test instance this amount of times
    """
    process_start_time = time.time()
    path = '/APTNotes'
    extracted_files = {}
    # ensure expected output folders exist
    for required_folder in ["/results", "/results/raw", "/results/processed", "/results/lsv"]:
        if not os.path.isdir('/iocextract/src'+ required_folder):
            os.mkdir('/iocextract/src'+ required_folder)

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
        print("-> iocextract test instance {} ".format(i))
        count = 0
        extract_avg_numerator = 0
        # files that for whatever reason cause iocextract to hang likely to do with pdf plumber
        skip_files = ["Elephantosis.pdf", "butterfly-corporate-spies-out-for-financial-gain.pdf"]
        
        for filename in os.listdir(path):
            if(count > maximum - 1):
                break
            if(filename in skip_files):
                continue

            # Extract text from pdf
            filepath = os.path.join(path, filename)
            content = convert_pdf_txt(filepath)
            
            # Extract Indicators of Compromise from text, recording time
            extracted_files[filename] = {}
            extract_start_time = time.time()
            extracted_files[filename]["urls"] = list(iocextract.extract_urls(content, refang=True))
            extracted_files[filename]["email_addresses"] = list(iocextract.extract_emails(content, refang=True))
            extracted_files[filename]["ipv4s"] = list(iocextract.extract_ipv4s(content, refang=True))
            extracted_files[filename]["ipv6s"] = list(iocextract.extract_ipv6s(content))
            extracted_files[filename]["md5s"] = list(iocextract.extract_md5_hashes(content))
            extracted_files[filename]["sha1s"] = list(iocextract.extract_sha1_hashes(content))
            extracted_files[filename]["sha256s"] = list(iocextract.extract_sha256_hashes(content))
            extracted_files[filename]["sha512s"] = list(iocextract.extract_sha512_hashes(content))
            extracted_files[filename]["yara"] = list(iocextract.extract_yara_rules(content))
            extract_avg_numerator += time.time() - extract_start_time
            
            count += 1

        process_end_time = time.time()

        # add some meta info on process run time
        extracted_files["meta"] = {
            "tool": "iocextract",
            "files_examined": count,
            "elapsed_time": process_end_time - process_start_time,
            "average_time": extract_avg_numerator / count,
        }

        print("iocextract scanned {} files".format(count))

        # used by machinae / when desired output is line separated observables
        all_iocs = set()
        for filename in extracted_files:
            if filename == 'meta': continue
            for ioc_type in extracted_files[filename]:
                all_iocs.update(extracted_files[filename][ioc_type])

        # lsv export (used by machinae)
        lsv_path = "/iocextract/src/results/lsv/"
        lsv_filename = "iocextract_lsv.txt"
        with open(lsv_path + lsv_filename, 'w') as lsv:
            lsv.write('\n'.join(all_iocs))

        # json export
        results_path = "/iocextract/src/results/raw/"
        results_filename = "iocextract_raw_{}_files_{}.json".format(count, 
            time.strftime('%H-%M-%S', time.localtime()))
        with open(results_path + results_filename, 'w') as fp:
            json.dump(extracted_files, fp)