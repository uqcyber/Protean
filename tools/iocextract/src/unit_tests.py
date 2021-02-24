#
# Copyright (c) 2020, 2021 Oracle and/or its affiliates. All rights reserved.
#

import unittest
import iocextract  # regex-based

class TestIOCExtract(unittest.TestCase):
    """
    Unit tests to verify which Indicators of Compromise iocextract correctly extracts
    as well as what defanging techniques it recognises.
    """

    ### Supported IOC Tests###
    def test_yara(self):
        content = "rule example { strings: $c0 = /[0-9a-fA-F]{20}/ condition: $c0 }"
        result = list(iocextract.extract_yara_rules(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

    def test_url(self):
        content = "https://www.example.com"
        result = list(iocextract.extract_urls(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

    def test_email(self):
        content = "me@example.com"
        result = list(iocextract.extract_emails(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

    def test_xmpp(self):
        content = "example@xmpp.com"
        result = list(iocextract.extract_emails(content))
        self.assertEqual(len(result), 1)

    def test_ip_email(self):
        content = "me@192.168.0.1.com"
        result = list(iocextract.extract_emails(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

    def test_ipv4(self):
        content = "192.168.0.1"
        result = list(iocextract.extract_ipv4s(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

    def test_ipv6(self):
        content = "2001:0db8:3c4d:0015:0000:0000:1a2f:1a2b"
        result = list(iocextract.extract_ipv6s(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

    def test_sha1(self):
        content = "62283808776ee974d7e7792ffa12eb90fe36556a"
        result = list(iocextract.extract_sha1_hashes(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

    def test_sha256(self):
        content = "c4ed9a5c3798260ebc2c43c02428cae33fe3dd59129ec82f50374b82a4e4907d"
        result = list(iocextract.extract_sha256_hashes(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

    def test_sha512(self):
        content = "2960827d026a8488fd663cd23b8d71957275c296fd8dfd47e84a820d864d172c2b34" \
            "19724d58d5151f597d1bf2a932a9a83a30aefc0dcc05a91d1f23fb747fab"
        result = list(iocextract.extract_sha512_hashes(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

    def test_MD5(self):
        content = "8d13ed81f15ff53688df90dd38cbd6d6"
        result = list(iocextract.extract_md5_hashes(content))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], content)

### Defanging Tests ###

    def test_defang_dot(self):
        content = "192.168.0.1"
        combinations = [
            ["\."],
            ["(.)", "(.", ".)"],
            ["[.]", "[.", ".]"],
        ]

        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace(".", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_ipv4s(defanged_content, refang=True))
                self.assertEqual(len(result), 1, "failed defang on: " + defang_style)
                self.assertEqual(result[0], content)
    
    def test_defang_unsupported_dot(self):
        content = "192.168.0.1"
        combinations = [
            ["(.(", ").(", ").)", ".("],
            ["[.[", "].[", "].]", ".[", "]."],
            ["{.{", "{.}", "}.{", "}.}", "{.", ".{", "}.", ".}"],
        ]

        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace(".", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_ipv4s(defanged_content, refang=True))
                self.assertNotEqual(len(result), 1, "should fail on defanging style : " + defang_style)
    
    def test_defang_at(self):
        content = "me@example.com"
        combinations = [
            ["(@)", "(@", "@)", ],
            ["[@]", "[@", "@]"],
            ["{@}", "{@", "@}"],
        ]

        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace("@", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_emails(defanged_content, refang=True))
                self.assertEqual(len(result), 1, "failed defang on: " + defang_style)
                self.assertEqual(result[0], content)
    
    def test_defang_unsupported_at(self):
        content = "me@example.com"
        combinations = [
            ["(@(", ")@(", ")@)", "@(", ")@"],
            ["[@[", "]@[", "]@]", "@[", "]@",],
            ["{@{", "}@{", "}@}", "@{", "}@",],
        ]

        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace("@", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_emails(defanged_content, refang=True))
                self.assertNotEqual(len(result), 1, "should fail on defanging style : " + defang_style)

    def test_defang_dot_slash_slash(self):
        content = "https://example.com"
        combinations = [
            [ "://)", "://("],
            [ "://]", "://["],
            [ "__"],
            [ ":\\\\"],
        ]
        #incorrectly refangsd on "://}" "://{"
        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace("://", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_urls(defanged_content, refang=True))
                self.assertEqual(len(result), 1, "failed defang on: " + defang_style)
                self.assertEqual(result[0], content, "incorrectly refanged")
    
    def test_defang_unsupported_dot_slash_slash(self):
        content = "https://www.example.com"
        combinations = [
            ["(://(", "(://)", ")://(", ")://)", "(://", ")://"],
            ["[://[", "[://]", "]://[", "]://]", "[://", "]://",],
            ["{://{", "{://}", "}://{", "}://}", "{://", "}://",],
        ]

        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace("://", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_urls(defanged_content, refang=True))
                self.assertNotEqual(len(result), 1, "should fail on defanging style : " + defang_style)
  
    def test_defang_unsupported_colon(self):
        content = "https://www.example.com"
        combinations = [
            ["(:(", "(:)", "):(", "):)", "(:", ":(", "):", ":)"],
            ["[:[", "[:]", "]:[", "]:]", "[:", ":[", "]:", ":]"],
            ["{:{", "{:}", "}:{", "}:}", "{:", ":{", "}:", ":}"],
        ]

        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace(":", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_urls(defanged_content, refang=True))
                self.assertNotEqual(len(result), 1, "should fail on defanging style : " + defang_style)

    def test_defang_http(self):
        content = "http://example.com"
        combinations = [
            ["(http", ")http",],
            ["[http", "]http",],
            ["{http", "}http",],
            ["hxxp"],
        ]
        #
        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace("http", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_urls(defanged_content, refang=True))
                self.assertEqual(len(result), 1, "failed defang on: " + defang_style)
                self.assertEqual(result[0], content, "incorrectly refanged")

    def test_defang_unsupported_http(self):
        content = "http://example.com"
        combinations = [
            ["(http(", "(http)", ")http(", ")http)",  "http(",  "http)"],
            ["[http[", "[http]", "]http[", "]http]",   "http(",  "http]"],
            ["{http{", "{http}", "}http{", "}http}",  "http{",  "http}"],
        ]

        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace("http", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_urls(defanged_content, refang=True))
                self.assertNotEqual(len(result), 1, "should fail on defanging style: " + defang_style)

    def test_defang_unsupported_comma(self):
        content = "192.168.0.1"
        combinations = [
            ["(,(", "(,)", "),(", "),)", "(,", ",(", "),", ",)"],
            ["[,[", "[,]", "],[", "],]", "[,", ",[", "],", ",]"],
            ["{,{", "{,}", "},{", "},}", "{,", ",{", "},", ",}"],
        ]

        for substitution_type in combinations:
            for defang_style in substitution_type:
                defanged_content = content.replace(".", defang_style)
                #print("checking: " + defanged_content)
                result = list(iocextract.extract_ipv4s(defanged_content, refang=True))
                self.assertNotEqual(len(result), 1, "should fail on defanging style : " + defang_style)

if __name__ == '__main__':
    unittest.main()