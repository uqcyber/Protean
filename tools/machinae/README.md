# Machinae
### Threat Intelligence Collection
###### *Installed Version: 1.4.9*
<img style="
display: block;
width: 250px;
margin: 0 auto;"
src=../../docs/images/machinae/machinae_io.png/>

[<span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #a9c4eb;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> MACHINAE </span>](https://github.com/HurricaneLabs/machinae) takes observables such as IP addresses, domains, URLS, email addresses, file hashes and SSL fingerprints, and collects intelligence from various public sources. 


###### Categorisation
To recommend which supported data sources should be utilized for different use cases, the list of default data sources were categorised and verified to work at the time of testing. The resulting categories are as follows:
+	**Network Information:** IP WHOIS
+	**Risk Indication:** SANS, VirusTotal URL Report, Fortinet Category
+	**Passive DNS**: ThreatCrowd IP Report, VirusTotal pDNS
+	**Malware Hash Detection:** VxVault, Cymru MHR, VirusTotal File Report
+	**Utility:** StopForumSpam, MACVendor

Of the functioning tools, the following are recommended to **disable**:
+ **SANS:** low response rates, weird output
+ **Cymru MHR:** no longer actively maintained
+ **VirusTotal**: lack of a working --delay flag is unfriendly to VirusTotal API limit of 4/min
    + use Protean's <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #facd62;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> DISPATCHER </span> to communicate with VirusTotal

#### Input(s)
Machinae supports the following inputs:
+ IPv4 Addresses
+ Fully Qualified Domain Names (FQDN)
+ URLs
+ Email Addresses
+ File Hashes
+ MAC addresses

#### Output(s)
The following demonstrates positive results from each working data source in Machinae.

```json
"sans": {
	"SANS attacks": "1" ,
	"SANS count": [
		"1",
		"1"
	],
	"SANS maxdate": "2020-12-28",	
	"SANS mindate": "2020-12-28",	
}

"vt_url": {
	"Date submitted": "2021-01-03 05:00:00",
	"Detected scanners": 0,
	"Total scanners": 83
}

"fortinet_classify": {
	"Fortinet URL Category": "Information Technology"
}

"threatcrowd_ip_report": {
	"Passive DNS": [
		"marcqualie.net",
		"2020-12-10"
	]
}

"vt_ip": {
	"pDNS data from VirusTotal": [
		"2012-12-23",
		"admin.yourdog.co.uk"
	]
}

"vxvault": {
	"Date found at VXVault": "01-01",
	"URL found at VXVault": "[Protean] URL redacted"
}

"cymru": {
	"Cymru MHR Detection Percent": [
		"1603988640",
		"49"
	]
}

"vt_hash": {
	"Date submitted": "2021-01-06 02:46:00",
	"Detected engines": 52,
	"Total engines": 70,
	"Scans": [
		"Elastic",
		"malicious (high confidence)"
	]
}

"stopforumspam": {
	"Spam email count": "10"
}

"macvendors": {
	"Mac Address Vendor": "Apple, Inc"
}
```

#### Note(s)
+ 11 / 22 default data sources are functional
+ 3 data sources use outdated regular expressions
+ 8 data sources are discontinued
+ no functioning tool supports IPv6 or SSL Fingerprints
+ --delay flag is non-functional (at time of testing)

#### Contributions
###### unit_tests.py
+ verification of which data sources are working and reproducibility of this information through unit tests
+ categorisation of data sources and subsequent recommendations
###### api_dispatcher.py
The API <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #facd62;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> DISPATCHER </span> was created to act as a ‘consumer’ to the generated outputs of <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
border-radius: 5px; 
background-image: linear-gradient(to right, #D76F84, #EF86C9, #9761DB);
padding: 0.25em; 
color: white;
"> PROTEAN</span>, polling three threat intelligence sources (OTX AlienVault, ThreatMiner and VirusTotal) with provided observables.
