# ioc-finder
### Grammar-based IOC Text Extraction
###### *Installed Version: 5.0.0*
<img style="
display: block;
width: 250px;
margin: 0 auto;"
src=../../docs/images/ioc-finder/ioc-finder_io.png/>


The [<span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #f0ccde;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> IOC-FINDER </span>](https://github.com/fhightower/ioc-finder) Python library utilizes a custom grammar ruleset to extract and refang Indicators of Compromise (or *Observables*) from bodies of text.

#### Input(s)
+ Text files parsable by Python

#### Output(s)
The method `find_iocs()` returns the following dictionary:

```json
{
    "asns": [],
    "attack_mitigations": {
        "enterprise": [],
        "mobile": []
    },
    "attack_tactics": {
        "enterprise": [],
        "mobile": [],
        "pre_attack": []
    },
    "attack_techniques": {
        "enterprise": [],
        "mobile": [],
        "pre_attack": []
    },
    "authentihashes": [],
    "bitcoin_addresses": [],
    "cves": [],
    "domains": [],
    "email_addresses": [],
    "email_addresses_complete": [],
    "file_paths": [],
    "google_adsense_publisher_ids": [],
    "google_analytics_tracker_ids": [],
    "imphashes": [],
    "ipv4_cidrs": [],
    "ipv4s": [],
    "ipv6s": [],
    "mac_addresses": [],
    "md5s": [],
    "monero_addresses": [],
    "phone_numbers": [],
    "registry_key_paths": [],
    "sha1s": [],
    "sha256s": [],
    "sha512s": [],
    "ssdeeps": [],
    "tlp_labels": [],
    "urls": [],
    "user_agents": [],
    "xmpp_addresses": []
}
```

#### Note(s)
+ will not correctly parse registry key paths where the last section contains white space
+ several observable types are in beta and may not reliably parse all text variants of an observable
+ parsing markdown with a domain surrounded by underscores will include the leading underscore

#### Contributions
###### unit_tests.py
Suite of unit tests used to verify supported Indicator of Compromise types and defanging techniques

###### performance_tests.py
Uses pdfs in the APTNotes repository to test each extraction tool, recording elapsed time and the average time it takes a tool to finish extracting a file.

Program arguments:
- argv[1] maximum: sets the maximum amount of files to attempt extraction of
- argv[2] repetitions: repeat the test instance this amount of times

Note the logic of repeating tests was moved to inside of performance_tests.py as ```docker exec``` has considerable set-up time if repeatedly called.

###### test_analysis.py
Takes the results from performance_tests.py, counts the number of observables and calculates average metrics across test instances

###### finder_protean.py
Similar to performance_tests.py but for the tool’s use within Protean, uses documents from the /protean_input folder