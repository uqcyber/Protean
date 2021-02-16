#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
import unittest
import machinae
import os
import json
import time

def validate_api(expected_keys, site_key, observable):
    """
        Helper method since testing all apis uses the same process.
        Runs Machinae and verifies that a result is returned, and the result
        is what is expected from machinae's config.
    """
    api_timeout = 5
    os.system('machinae -oJ -f unit_result.json -s' + site_key + " " + observable)
    
    # 5s timeout for API call returning
    count = 0
    while not os.path.exists(result_path):
        if(count > api_timeout):
            print("No response from api in {}s".format(api_timeout))
            return False
        time.sleep(1)
        count += 1

    # Check if results exist, and if it has expected structure
    with open('unit_result.json', 'r') as f:
        line = f.readline()
        result = json.loads(line)
        if len(result['results']) == 0:
            print("API returned empty results")
            return False
        for k in expected_keys: 
            if k not in result['results']:
                print("{} not found in {}".format(k, result.keys()))
                return False
    return True

class TestMachinae(unittest.TestCase):
    """
    Unit tests to confirm the selected data sources are working.
    """

    def test_ipwhois(self):
        expected_keys = ["ASN Information", "Network Information", "Registration Info", "Registration Locality", "Abuse Email"]
        self.assertTrue(validate_api(expected_keys, "ipwhois", "5.199.130.188"))
        os.remove("./unit_result.json")

    def test_sans(self):
        expected_keys = ["SANS attacks", "SANS count", "SANS maxdate", "SANS mindate"]
        self.assertTrue(validate_api(expected_keys, "sans", ipv4))
        os.remove("./unit_result.json")
       
    def test_fortinet_classify(self):
        expected_keys = ["Fortinet URL Category"]
        self.assertTrue(validate_api(expected_keys, "fortinet_classify", url))
        os.remove("./unit_result.json")

    def test_vt_ip(self):
        expected_keys = ["pDNS data from VirusTotal"]
        self.assertTrue(validate_api(expected_keys, "vt_ip", "104.27.128.139"))
        os.remove("./unit_result.json")

    def test_vt_domain(self):
        expected_keys = ["pDNS data from VirusTotal"]
        self.assertTrue(validate_api(expected_keys, "vt_domain", domain))
        os.remove("./unit_result.json")

    def test_vt_url(self):
        expected_keys = ["Date submitted", "Detected scanners", "Total scanners"]
        self.assertTrue(validate_api(expected_keys, "vt_url", url))
        os.remove("./unit_result.json")

    def test_vt_hash(self):
        expected_keys = ["Date submitted", "Detected engines", "Total engines", "Scans"]
        self.assertTrue(validate_api(expected_keys, "vt_hash", sha256))
        os.remove("./unit_result.json")

    def test_vxvault(self):
        expected_keys = ["Date found at VXVault", "URL found at VXVault"]
        self.assertTrue(validate_api(expected_keys, "vxvault", "5C96362633FDD8B984535046FDF2BA4A"))
        os.remove("./unit_result.json")

    def test_stopforumspam(self):
        expected_keys = ["Spam email count"]
        self.assertTrue(validate_api(expected_keys, "stopforumspam", email))
        os.remove("./unit_result.json")

    def test_cymru_mhr(self):
        expected_keys = ["Cymru MHR Detection Percent"]
        self.assertTrue(validate_api(expected_keys, "cymru_mhr", "30ed21fa6e96f58bcd0c16e4f52ace82"))
        os.remove("./unit_result.json")

    def test_threatcrowd_ip_report(self):
        expected_keys = ["Passive DNS"]
        self.assertTrue(validate_api(expected_keys, "threatcrowd_ip_report", "188.40.75.132"))
        os.remove("./unit_result.json")

    def test_macvendor(self):
        expected_keys = ["Mac Address Vendor"]
        self.assertTrue(validate_api(expected_keys, "macvendors", mac))
        os.remove("./unit_result.json")

if __name__ == '__main__':
    
    # Observables
    ipv4 = "45.227.255.205"
    sha256 = "DB1AEC5222075800EDA75D7205267569679B424E5C58A28102417F46D3B5790D"
    mac = "00:0a:95:9d:68:16"
    md5 = "35F86945CA3277C1531EBD23A10D7C16"
    email = "divyarsw@gmail.com"
    url = "http://www.github.com"
    short_url = "http://bit.ly/TCm6Uy"
    domain = "github.com"
    result_path = './unit_result.json'
    unittest.main()