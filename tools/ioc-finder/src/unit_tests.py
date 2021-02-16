#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#
import unittest
from ioc_finder import find_iocs

class TestIOCFinder(unittest.TestCase):
    """
    Unit tests to verify which Indicators of Compromise ioc-finder correctly extracts
    as well as what defanging techniques it recognises.
    """

    ### Supported IOCs ###
    def test_url(self):
        content = "https://www.example.com"
        result = find_iocs(content)
        self.assertEqual(result['urls'][0], content)

    def test_email(self):
        content = "me@example.com"
        result = find_iocs(content)
        self.assertEqual(result['email_addresses'][0], content)

    def test_xmpp(self):
        content = "me@xmpp.com"
        result = find_iocs(content)
        self.assertEqual(result['xmpp_addresses'][0], content)

    def test_ip_email(self):
        content = "me@192.168.0.1.com"
        result = find_iocs(content)
        self.assertEqual(result['email_addresses'][0], content)
    
    def test_domain(self):
        content = "www.example.com"
        result = find_iocs(content)
        self.assertEqual(result['domains'][0], content)

    def test_cidr(self):
        content = "192.168.0.1/14"
        result = find_iocs(content)
        self.assertEqual(result['ipv4_cidrs'][0], content)

    def test_ipv4(self):
        content = "192.168.0.1"
        result = find_iocs(content)
        self.assertEqual(result['ipv4s'][0], content)

    def test_ipv6(self):
        content = "2001:0db8:3c4d:0015:0000:0000:1a2f:1a2b"
        result = find_iocs(content)
        self.assertEqual(result['ipv6s'][0], content)

    def test_MD5(self):
        content = "8d13ed81f15ff53688df90dd38cbd6d6"
        result = find_iocs(content)
        self.assertEqual(result['md5s'][0], content)

    def test_sha1(self):
        content = "62283808776ee974d7e7792ffa12eb90fe36556a"
        result = find_iocs(content)
        self.assertEqual(result['sha1s'][0], content)

    def test_sha256(self):
        content = "c4ed9a5c3798260ebc2c43c02428cae33fe3dd59129ec82f50374b82a4e4907d"
        result = find_iocs(content)
        self.assertEqual(result['sha256s'][0], content)

    def test_sha512(self):
        content = "2960827d026a8488fd663cd23b8d71957275c296fd8dfd47e84a820d864d172c2b34" \
            "19724d58d5151f597d1bf2a932a9a83a30aefc0dcc05a91d1f23fb747fab"
        result = find_iocs(content)
        self.assertEqual(result['sha512s'][0], content)

    def test_imphash(self):
        content = "Imphash: b8bb385806b89680e13fc0cf24f4431e"
        result = find_iocs(content)
        self.assertEqual(result['imphashes'][0], "b8bb385806b89680e13fc0cf24f4431e")

    def test_authentihash(self):
        content = "authentihash c4ed9a5c3798260ebc2c43c02428cae33fe3dd59129ec82f50374b82a4e4907d"
        result = find_iocs(content)
        self.assertEqual(result['authentihashes'][0], "c4ed9a5c3798260ebc2c43c02428cae33fe3dd59129ec82f50374b82a4e4907d")

    def test_ssdeeps(self):
        content = "768:v7XINhXznVJ8CC1rBXdo0zekXUd3CdPJxB7mNmDZkUKMKZQbFTiKKAZTy:ShT8C+fuioHq1KEFoAU"
        result = find_iocs(content)
        self.assertEqual(result['ssdeeps'][0], content)
        
    def test_asn(self):
        content = "ASN7160"
        result = find_iocs(content)
        self.assertEqual(result['asns'][0], content)

    def test_cve(self):
        content = "CVE-2014-1234"
        result = find_iocs(content)
        self.assertEqual(result['cves'][0], content)

    def test_registry_key_path(self):
        content = "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows"
        result = find_iocs(content)
        self.assertEqual(result['registry_key_paths'][0], content)

    def test_google_adsense_publisher_id(self):
        content = "pub-1234567891234567"
        result = find_iocs(content)
        self.assertEqual(result['google_adsense_publisher_ids'][0], content)

    def test_google_analytics_tracker_id(self):
        content = "UA-000000-2"
        result = find_iocs(content)
        self.assertEqual(result['google_analytics_tracker_ids'][0], content)

    def test_bitcoin_address(self):
        content = "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2 " \
            "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy " \
            "bc1qnkyhslv83yyp0q0suxw0uj3lg9drgqq9c0auzc"
        result = find_iocs(content)
        self.assertEqual(len(result['bitcoin_addresses']), 3)

    def test_monero_address(self):
        content = "4AdUndXHHZ6cfufTMvppY6JwXNouMBzSkbLYfpAV5Usx3skxNgYeYTRj5UzqtR"\
            "eoS44qo9mtmXCqY45DJ852K5Jv2684Rge"
        result = find_iocs(content)
        self.assertEqual(result['monero_addresses'][0], "4AdUndXHHZ6cfufTMvppY6JwXNouMBzSkb"\
            "LYfpAV5Usx3skxNgYeYTRj5UzqtReoS44qo9mtmXCqY45DJ852K5Jv2684Rge")

    def test_mac_address(self):
        content = "00:0a:95:9d:68:16"
        result = find_iocs(content)
        self.assertEqual(result['mac_addresses'][0], content)

    @unittest.skip
    def test_user_agents(self):
        #what is a user agent
        content = ""
        result = find_iocs(content)
        self.assertEqual(result['user_agents'][0], content)

    def test_file_path(self):
        content = "C:\\Users\\name\Desktop\\virus.exe"
        result = find_iocs(content)
        self.assertEqual(result['file_paths'][0], content)

    def test_phone_number(self):
        content = "555-1234"
        result = find_iocs(content)
        self.assertEqual(result['phone_numbers'][0], content)

    def test_tlp_label(self):
        content = "TLP:RED"
        result = find_iocs(content)
        self.assertEqual(result['tlp_labels'][0], content)

    @unittest.skip
    def test_mitre_attack(self):
        content = ""
        result = find_iocs(content)
        self.assertEqual(result[''][0], "")

    ### Expected failures for ioc-finder ###
    @unittest.expectedFailure
    def test_yara(self):
        content = "rule example { strings: $c0 = /[0-9a-fA-F]{20}/ condition: $c0 }"
        grammar_dict = find_iocs(content)
        self.assertEqual(len(grammar_dict), 1, "yara unsupported")

### Defanging Tests ###
    def test_defang_dot(self):
        #note ). is excluded as it is deemed a valid end to a sentence
        content = "192.168.0.1"
        combinations = [
            ["(.(", "(.)", ").(", ").)", "(.", ".(", ".)"],
            ["[.[", "[.]", "].[", "].]", "[.", ".[", "].", ".]"],
            ["{.{", "{.}", "}.{", "}.}", "{.", ".{", "}.", ".}"],
            ["\."],
        ]
        
        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace(".", defang_style)
                result = find_iocs(defanged_content)
                self.assertEqual(len(result['ipv4s']), 1, "failed on defanging style: " + defang_style)
                self.assertEqual(result['ipv4s'][0], content, "incorrectly refanged content")

    def test_defang_at(self):
        content = "me@example.com"
        combinations = [
            ["(@(", "(@)", ")@(", ")@)", "(@", "@(", "@)"],
            ["[@[", "[@]", "]@[", "]@]", "[@",  "]@", "@]"],
            ["{@{", "{@}", "}@{", "}@}", "{@", "@{", "}@", "@}"],
        ]
        #unsupported = "-@-"
        
        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace("@", defang_style)
                result = find_iocs(defanged_content)
                self.assertEqual(len(result['email_addresses']), 1, "failed on defanging style: " + defang_style)
                self.assertEqual(result['email_addresses'][0], content, "incorrectly refanged content")

    def test_defang_dot_dot_slash(self):
        content = "https://example.com"
        combinations = [
            ["(://(", "(://)", ")://(", ")://)", "(://", "://(","://(", "://)"],
            ["[://[", "[://]", "]://[", "]://]", "[://",  "://(", "]://", "://]"],
            ["{://{", "{://}", "}://{", "}://}", "{://", "://{", "}://", "://}"],
        ]
        
        #unsupported __ & :\\
        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace("://", defang_style)
                result = find_iocs(defanged_content)
                self.assertEqual(len(result['urls']), 1, "failed on defanging style: " + defang_style)
                self.assertEqual(result['urls'][0], content, "incorrectly refanged content")

    def test_defang_colon(self):
        content = "https://example.com"
        combinations = [
            ["(:(", "(:)", "):(", "):)", "(:", ":(","):", ":)"],
            ["[:[", "[:]", "]:[", "]:]", "[:",  ":(", "]:", ":]"],
            ["{:{", "{:}", "}:{", "}:}", "{:", ":{", "}:", ":}"],
        ]
        
        #unsupported
        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace(":", defang_style)
                result = find_iocs(defanged_content)
                self.assertEqual(len(result['urls']), 1, "failed on defanging style: " + defang_style)
                self.assertEqual(result['urls'][0], content, "incorrectly refanged content")

    def test_defang_http(self):
        content = "http://example.com"
        combinations = [
            ["(http(", "(http)", ")http(", ")http)", "(http", "http(",")http", "http)"],
            ["[http[", "[http]", "]http[", "]http]", "[http",  "http(", "]http", "http]"],
            ["{http{", "{http}", "}http{", "}http}", "{http", "http{", "}http", "http}"],
            ["hxxp"],
        ]
        
        #unsupported
        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace("http", defang_style)
                result = find_iocs(defanged_content)
                self.assertEqual(len(result['urls']), 1, "failed on defanging style: " + defang_style)
                self.assertEqual(result['urls'][0], content, "incorrectly refanged content")
   
    
    def test_defang_comma(self):
        #note ), is excluded as it is deemed a valid grammar in a normal sentence
        content = "192.168.0.1"
        combinations = [
            ["(,(", "(,)", "),(", "),)", "(,", ",(", ",)"],
            ["[,[", "[,]", "],[", "],]", "[,", ",[", "],", ",]"],
            ["{,{", "{,}", "},{", "},}", "{,", ",{", "},", ",}"],
        ]
        
        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace(".", defang_style)
                result = find_iocs(defanged_content)
                self.assertEqual(len(result['ipv4s']), 1, "failed on defanging style: " + defang_style)
                self.assertEqual(result['ipv4s'][0], content, "incorrectly refanged content")

if __name__ == '__main__':
    unittest.main()