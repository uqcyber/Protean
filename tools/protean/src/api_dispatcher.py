#!/usr/bin/env python3
#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
import os
import json
from OTXv2 import OTXv2
import IndicatorTypes
import requests
import copy
import vt

class OtxHandler:
    """
    Handler class for connecting to and using the OTX API for threat intelligence.
    """
    def __init__(self, api_key):
        self.limit_per_min = -1 # no limit
        self.otx = OTXv2(api_key)
        self.output = {
            "ipv4s": {},
            "ipv6s": {},
            "domains": {},
            "md5s": {},
            "sha1s": {},
            "sha256s": {},
            "urls": {},
            "cves": {},
        }
        # maps an indicator type to the reference required by OTXv2
        self.supported_indicators = {
            "ipv4s": IndicatorTypes.IPv4,
            "ipv6s": IndicatorTypes.IPv6,
            "domains": IndicatorTypes.DOMAIN,
            "md5s": IndicatorTypes.FILE_HASH_MD5,
            "sha1s": IndicatorTypes.FILE_HASH_SHA1,
            "sha256s": IndicatorTypes.FILE_HASH_SHA256,
            "urls": IndicatorTypes.URL,
            "cves": IndicatorTypes.CVE,
        }

    def run(self, indicators, indicator_type, maximum):
        """
        Utilises the OTXv2 library to query and store results
        relating to threat intelligence observables from the OTX API.
        """
        if indicator_type not in self.supported_indicators:
            print(f'[OTX] does not support {indicator_type}')
            exit()

        if indicator_type not in indicators:
            print(f'[OTX] {indicator_type} not found in provided observables')
            exit()

        print(f'[OTX] Querying a maximum of {maximum} out of {len(indicators[indicator_type])} {indicator_type}')
        count = 0
        for i in indicators[indicator_type]:
            if count == maximum:
                break

            # used to get an indicator when in format {value, source}
            if isinstance(i, dict):
                i = i['value']

            details = self.otx.get_indicator_details_full(
                IndicatorTypes.FILE_HASH_MD5, i)
            self.output[indicator_type][i] = details

            count += 1
        print("[OTX] complete")

class ThreatMinerHandler:
    """
    Handler class for connecting to and using the ThreatMiner API for threat intelligence.
    """
    def __init__(self):
        self.limit_per_min = 10
        self.output = {
            "ipv4s": {},
            "md5s": {},
            "sha1s": {},
            "sha256s": {},
            "imphashes": {},
            "ssdeeps": {},
            "email_addresses": {},
            "domains": {},
        }
        # maps indicator type names to indicator_ids used in API call
        self.supported_indicators = {
            "ipv4s": "host",
            "md5s": "sample",
            "sha1s": "sample",
            "sha256s": "sample",
            "imphashes": "imphash",
            "ssdeeps": "ssdeep",
            "email_addresses": "emails",
            "domains": "domain",
        }
        # maps indicator_ids to rt flags
        self.indicator_rts = {
            "domain": {
                1: 'whois',
                2: 'passive dns',
                3: 'example query uri',
                4: 'related samples',
                5: 'subdomains',
                6: 'report tagging',
            },
            "host": {
                1: 'whois',
                2: 'passive dns',
                3: 'URIs',
                4: 'related samples',
                5: 'SSL certificates',
                6: 'report tagging',
            },
            "sample": {
                1: 'metadata',
                2: 'http traffic',
                3: 'hosts',
                4: 'mutants',
                5: 'registry keys',
                6: 'av detections',
                7: 'report tagging',
            },
            "imphash": {
                1: 'samples',
                2: 'report tagging',
            },
            "ssl": {
                1: 'hosts',
                2: 'report tagging',
            },
            "emails": {
                1: 'domains',
            },
        }
        self.request_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.130 Safari/537.36'
            }

    def run(self, indicators, indicator_type, maximum):
        '''
        ThreatMiner query format:
            https://api.threatminer.org/v2/{indicator_id}.php?q={observable}&rt={rt}

        indicator_type  indicator_id
        domains         domain
        ipv4s           host
        hashes          sample  (sha1, sha256, sha512, ssdeep, imphash)
        imphashes       imphash
        ssdeeps         ssdeep
        email_addresses email

        rt flag numbers and their descriptions for each indicator_id is represented in the indicators_rts dictionary
        '''

        if indicator_type not in self.supported_indicators:
            print(f'[ThreatMiner] does not support {indicator_type}')
            exit()

        if indicator_type not in indicators:
            print(f'[ThreatMiner] {indicator_type} not found in provided observables')
            exit()

        print(f'[ThreatMiner] Querying a maximum of {maximum} out of {len(indicators[indicator_type])} {indicator_type}')
        count = 0
        for i in indicators[indicator_type]:
            if count == maximum:
                break

            # used to get an indicator when in format {value, source}
            if isinstance(i, dict):
                i = i['value']

            indicator_id = self.supported_indicators[indicator_type]

            for flag in self.indicator_rts[indicator_id]:
                url = f"https://api.threatminer.org/v2/{indicator_id}.php?q={i}&rt={flag}"
                r = requests.get(url, headers=self.request_headers)
                j = json.loads(r.text)
                
                flag_desc = self.indicator_rts[indicator_id][flag]
                if j.get('status_code') == '200':  # response found
                    print(f'[ThreatMiner] Success! (Observable: {i} | Flag: {flag})')
                    if flag_desc not in self.output[indicator_type]:
                        self.output[indicator_type][flag_desc] = {}
                    self.output[indicator_type][flag_desc][i] = j.get('results')
                else:
                    status_code = j.get('status_code')
                    print(f'[ThreatMiner] Failure! (Observable: {i} | ID: {indicator_id} | Flag: {flag} | Status Code: {status_code})')

            count += 1
        print("[ThreatMiner] complete")

class VirusTotalHandler:
    """
    Handler class for connecting to and using the VirusTotal API for threat intelligence.
    Docs: https://developers.virustotal.com/v3.0/
    API Request Limitations:
        Rate = 4 requests / minute
        Maximum = 500 requests / day
    """
    def __init__(self, api_key):
        self.limit_per_min = 4 #doesn't seem accurate?
        self.vt_client = vt.Client(api_key)
        self.output = {
            "ipv4s": {},
            "md5s": {},
            "sha1s": {},
            "sha256s": {},
            "urls": {},
            "domains": {},
        }
        # maps supported indicators to their API object reference id
        self.supported_indicators = {
            "ipv4s": "ip_addresses",
            "md5s": "files",
            "sha1s": "files",
            "sha256s": "files",
            "urls": "urls",
            "domains": "domains",
        }

    def run(self, indicators, indicator_type, maximum):
        """
        Utilises the vt-py library to query and store results
        relating to threat intelligence observables from the VirusTotal v3 API.
        """
        if maximum > 500:
            print(f'[VirusTotal] {maximum} > 500 | maximum of 500 API calls a day for free accounts')
            maximum = 500

        if indicator_type not in self.supported_indicators:
            print(f'[VirusTotal] does not support {indicator_type}')
            exit()

        if indicator_type not in indicators:
            print(f'[VirusTotal] {indicator_type} not found in provided observables')
            exit()

        print(f'[VirusTotal] Querying a maximum of {maximum} out of {len(indicators[indicator_type])} {indicator_type}')
        count = 0
        for i in indicators[indicator_type]:
            if count == maximum:
                break
            # used to get an indicator when in format {value, source}
            if isinstance(i, dict):
                i = i['value']

            # required from vt-py
            if indicator_type == "urls":
                i = vt.url_id(i)

            try:
                req = f'/{self.supported_indicators[indicator_type]}/{i}'
                res = self.vt_client.get_object(req)
                print(f"[VirusTotal] Success! {i}")
                self.output[indicator_type][i] = {}
                self.output[indicator_type][i]['last_analysis_stats'] = res.last_analysis_stats
                self.output[indicator_type][i]['last_analysis_results'] = res.last_analysis_results
                # note: according to the docs, virustotal has a 4req/min limit, but I have not encountered any rate limit
                # if this becomes an issue in the future, put a sleep() here
            except vt.error.APIError as e:
                if e.code == 'NotFoundError':
                    print(f"[VirsTotal] Failure! {i}")
                    pass
                else:
                    print("[VirusTotal] API Error:", e)
                continue
            except Exception as e:
                print("[VirusTotal] Something unexpected went wrong: ", e)
            count += 1

        self.vt_client.close()
        print("[VirusTotal] complete")

def loadObservables():
    '''
    Open the global_collation JSON outputted by the Protean pipeline.
    Returns only the extracted_iocs portion of the JSON
    '''
    with open(os.path.join(results_path, 'global_collation.json'), 'r') as fp:
        protean_json = json.load(fp)

    if 'extracted_iocs' in protean_json:
        return protean_json['extracted_iocs']
    elif 'iocextract' in protean_json:
        return protean_json['iocextract']
    else:
        return protean_json['ioc-finder']

if __name__ == '__main__':
    """
    The dispatcher provides methods to use the Protean's results (specifically observables extracted
    by iocextract or ioc-finder)
    """
    results_path = os.path.dirname(__file__) + "/results/"
    observables = loadObservables()

    # API Keys
    otx_key = None
    vt_key = None
    config_path = os.path.dirname(os.path.dirname(__file__)) + "/config/"
    print(config_path)
    with open(config_path + "api_keys.json", 'r') as fp:
        api_keys = json.load(fp)

    otx_key = api_keys.get('otx_api', None)
    vt_key = api_keys.get('vt_api', None)

    if otx_key == None:
        print("OTX API Key not found")

    if vt_key == None:
        print("VT API Key not found")

    # Instantiate Classes
    otx_handler = OtxHandler(otx_key)
    tm_handler = ThreatMinerHandler()
    vt_handler = VirusTotalHandler(vt_key)

    # Run API for observables types in their respective filter
    with open(config_path + "api_filters.json", 'r') as fp:
        api_filters = json.load(fp)

    supported_apis = {
        'otx': otx_handler.run,
        'threatminer': tm_handler.run,
        'virustotal': vt_handler.run
    }

    for api in supported_apis:
        for ioc_type in api_filters[api]:
            if ioc_type == "max_requests_per_type":
                continue
            if api_filters[api][ioc_type] == True:
                supported_apis[api](observables, ioc_type, api_filters[api]["max_requests_per_type"])

    # JSON export
    results = {
        "otx_api_results": otx_handler.output,
        "threatminer_api_results": tm_handler.output,
        "virustotal_api_results": vt_handler.output,
    }

    print("[APIDispatcher] Complete")
    with open(results_path + "api_outputs/api_results.json", 'w') as fp:
        json.dump(results, fp)
