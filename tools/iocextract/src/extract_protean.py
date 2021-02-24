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
    Uses iocextract to extract observables from pdfs in the /protean_input folder, recording elapsed time
    and the average time it takes iocextract to finish extrating a file.
    """
    process_start_time = time.time()
    path = '/protean_input'
    extracted_files = {}

    # ensure expected output folders exist
    for required_folder in ["/raw", "/lsv"]:
        if not os.path.isdir('/iocextract_vol/'+ required_folder):
            os.mkdir('/iocextract_vol/'+ required_folder)

    count = 0
    extract_avg_numerator = 0
    for filename in os.listdir(path):
        # Extract text from pdf
        filepath = os.path.join(path, filename)
        content = convert_pdf_txt(filepath)
        #TODO: add support for other file types

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
        "tool": "ioc-finder",
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
    lsv_path = "/iocextract_vol/lsv/"
    lsv_filename = "iocextract_lsv.txt"
    with open(lsv_path + lsv_filename, 'w') as lsv:
        lsv.write('\n'.join(all_iocs))

    # json export
    results_path = "/iocextract_vol/raw/"
    results_filename = "iocextract_results.json"
    with open(results_path + results_filename, 'w') as fp:
        json.dump(extracted_files, fp)