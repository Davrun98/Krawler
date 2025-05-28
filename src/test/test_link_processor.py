import unittest

from instance_pooler.pooler import Pooler
from page_loader.loader import construct_page_loader
from link_processor.processor import LinkProcessor, LinkProcessorConfiguration


def construct_link_processor(config: dict) -> LinkProcessor:
    page_loader_pool = Pooler(construct_page_loader)
    lp_config = LinkProcessorConfiguration(page_loader_pool, config["subdomain"], config["host"])

    return LinkProcessor(lp_config)


class Testing(unittest.IsolatedAsyncioTestCase):
    async def test_format_relative_link(self):
        test_cases = [
            {
                "name": "domain",
                "processor_config": {
                    "subdomain": "",
                    "host": "example-domain.com"
                },
                "parent_link": "example-domain.com/",
                "link_input_expected_output_pairs": {
                    "relative/path": "www.example-domain.com/relative/path",
                    "/relative/path": "www.example-domain.com/relative/path",
                    "./relative/path": "www.example-domain.com/./relative/path",
                    "../relative/path": "www.example-domain.com/../relative/path"
                }
            },
            {
                "name": "subdomain and domain",
                "processor_config": {
                    "subdomain": "www",
                    "host": "example-domain.com"
                },
                "parent_link": "example-domain.com/",
                "link_input_expected_output_pairs": {
                    "relative/path": "www.example-domain.com/relative/path",
                    "/relative/path": "www.example-domain.com/relative/path",
                    "./relative/path": "www.example-domain.com/./relative/path",
                    "../relative/path": "www.example-domain.com/../relative/path"
                }
            },
            {
                "name": "subdomain, domain, and existing path",
                "processor_config": {
                    "subdomain": "www",
                    "host": "example-domain.com"
                },
                "parent_link": "example-domain.com/existing/path",
                "link_input_expected_output_pairs": {
                    "relative/path": "www.example-domain.com/existing/path/relative/path",
                    "/relative/path": "www.example-domain.com/existing/path/relative/path",
                    "./relative/path": "www.example-domain.com/existing/path/./relative/path",
                    "../relative/path": "www.example-domain.com/existing/path/../relative/path",
                    "relative/path/file.ext": "www.example-domain.com/existing/path/relative/path/file.ext"
                }
            },
            {
                "name": "existing path with filename",
                "processor_config": {
                    "subdomain": "www",
                    "host": "example-domain.com"
                },
                "parent_link": "example-domain.com/existing/path/filename.ext",
                "link_input_expected_output_pairs": {
                    "relative/path": "www.example-domain.com/existing/path/relative/path",
                    "/relative/path": "www.example-domain.com/existing/path/relative/path",
                    "./relative/path": "www.example-domain.com/existing/path/./relative/path",
                }
            }
        ]

        for test_case in test_cases:
            parent_link = test_case["parent_link"]
            link_input_expected_output_pairs: dict = test_case["link_input_expected_output_pairs"]

            processor = construct_link_processor(test_case["processor_config"])

            for input_link, expected in link_input_expected_output_pairs.items():
                out = await processor.format_relative_link(parent_link, input_link)
                self.assertEqual(out, expected)

    async def test_evaluate_link(self):
        test_cases = [
            {
                "name": "relative links",
                "processor_config": {
                    "subdomain": "",
                    "host": "example-domain.com"
                },
                "link_input_expected_output_pairs": {
                    "relative/path": True,
                    "/relative/path": True,
                    "./relative/path": True,
                    "../relative/path": True
                }
            },
            {
                "name": "default subdomain",
                "processor_config": {
                    "subdomain": "",
                    "host": "example-domain.com"
                },
                "link_input_expected_output_pairs": {
                    "example-domain.com": True,
                    "http://www.example-domain.com": True,
                    "www.example-domain.com/any/path": True, 
                    "other.example-domain.com": False,
                    "thirdparty.com": False,
                }
            },
            {
                "name": "alternate subdomain",
                "processor_config": {
                    "subdomain": "other",
                    "host": "example-domain.com"
                },
                "link_input_expected_output_pairs": {
                    "other.example-domain.com": True,
                    "example-domain.com": False,
                    "http://other.example-domain.com": True,
                    "http://www.example-domain.com": False,
                    "other.example-domain.com/any/path": True, 
                    "www.example-domain.com/any/path": False, 
                    "other.thirdparty.com": False,
                }
            },
            {
                "name": "multiple subdomains",
                "processor_config": {
                    "subdomain": "other.subdomain",
                    "host": "example-domain.com"
                },
                "link_input_expected_output_pairs": {
                    "other.subdomain.example-domain.com": True,
                    "other.example-domain.com": False,
                    "http://other.subdomain.example-domain.com": True,
                    "http://other.example-domain.com": False,
                    "other.subdomain.example-domain.com/any/path": True, 
                    "other.example-domain.com/any/path": False, 
                    "other.subdomain.thirdparty.com": False,
                }
            }
        ]

        for test_case in test_cases:
            link_input_expected_output_pairs = test_case["link_input_expected_output_pairs"]

            processor = construct_link_processor(test_case["processor_config"])

            for input_link, expected in link_input_expected_output_pairs.items():
                # print(f'{test_case["name"]}: {input_link}')
                out, _ = await processor.evaluate_link("www.example-domain.com", input_link)
                self.assertEqual(out, expected)