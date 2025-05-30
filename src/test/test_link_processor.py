import unittest

from test.mocks.mock_pooler import MockPooler
from test.mocks.mock_page_loader import MockPageLoader, construct_mock_page_loader
from link_processor.processor import LinkProcessor, LinkProcessorConfiguration
from test.common import test_out


def construct_link_processor(config: dict) -> LinkProcessor:
    page_loader_pool = MockPooler(construct_mock_page_loader)
    lp_config = LinkProcessorConfiguration(page_loader_pool, config["subdomain"], config["host"])

    return LinkProcessor(lp_config)


class Testing(unittest.IsolatedAsyncioTestCase):
    async def test_format_relative_link(self):
        test_out.log_starting_test_set("LinkProcessor - test format relative link")

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
            test_out.log_starting_test(test_case["name"])

            parent_link = test_case["parent_link"]
            link_input_expected_output_pairs: dict = test_case["link_input_expected_output_pairs"]

            processor = construct_link_processor(test_case["processor_config"])

            for input_link, expected in link_input_expected_output_pairs.items():
                # print(f'{test_case["name"]}: {input_link}')
                out = processor.format_relative_link(parent_link, input_link)
                self.assertEqual(out, expected)

    async def test_evaluate_link(self):
        test_out.log_starting_test_set("LinkProcessor - test evaluate link")

        test_cases = [
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
            test_out.log_starting_test(test_case["name"])

            link_input_expected_output_pairs = test_case["link_input_expected_output_pairs"]

            processor = construct_link_processor(test_case["processor_config"])

            for input_link, expected in link_input_expected_output_pairs.items():
                # print(f'{test_case["name"]}: {input_link}')
                out = processor.evaluate_link(input_link)
                self.assertEqual(out, expected)

    async def test_process_link(self):
        test_out.log_starting_test_set("LinkProcessor - test process link")

        test_cases = [
            {
                "name": "Process link given: www.example-domain.com",
                "processor_config": {
                    "subdomain": "www",
                    "host": "example-domain.com"
                },
                "expected_url": "www.example-domain.com",
                "page_loader_response": [
                    "this link is not going to be detected: www.not-detected.com/not/this/one",
                    "<a href='www.thirdparty.com'>this link should show in all_links</a>",
                    "<a href='www.thirdparty.com/with/path'>this link should show in all_links</a>",
                    "<a href='//third-party.com'>this link should show in all_links</a>",
                    "<a href='subdomain.example-domain.com'>this link should show in all_links</a>",
                    "<a href='https://www.example-domain.com/path'>this link should show in both lists</a>",
                    "<a href='www.example-domain.com/path'>this link should show in both lists</a>",
                    "<a href='example-domain.com/path'>this link should show in both lists</a>",
                    "<a href='/relative/path'>this link should show in both lists with the subdomain and host attached</a>",
                    "<!--<a href='www.example-domain.com/commented/anchor'>this link will show in both lists and I'm sad about it</a>-->"
                ],
                "expected_all_links": [
                    "www.thirdparty.com",
                    "www.thirdparty.com/with/path",
                    "//third-party.com",
                    "subdomain.example-domain.com",
                    "https://www.example-domain.com/path",
                    "www.example-domain.com/path",
                    "example-domain.com/path",
                    "www.example-domain.com/relative/path",
                    "www.example-domain.com/commented/anchor"
                ],
                "expected_local_links": [
                    "https://www.example-domain.com/path",
                    "www.example-domain.com/path",
                    "example-domain.com/path",
                    "www.example-domain.com/relative/path",
                    "www.example-domain.com/commented/anchor"
                ]
            },
            {
                "name": "Process link given example-domain.com",
                "processor_config": {
                    "subdomain": "",
                    "host": "example-domain.com"
                },
                "expected_url": "example-domain.com",
                "page_loader_response": [
                    "<a href='subdomain.example-domain.com'>this link should show in all_links</a>",
                    "<a href='https://www.example-domain.com/path'>this link should show in both lists</a>",
                    "<a href='www.example-domain.com/path'>this link should show in both lists</a>",
                    "<a href='example-domain.com/path'>this link should show in both lists</a>",
                    "<a href='/relative/path'>this link should show in both lists with 'www.' + the host attached</a>",
                ],
                "expected_all_links": [
                    "subdomain.example-domain.com",
                    "https://www.example-domain.com/path",
                    "www.example-domain.com/path",
                    "example-domain.com/path",
                    "www.example-domain.com/relative/path",
                ],
                "expected_local_links": [
                    "https://www.example-domain.com/path",
                    "www.example-domain.com/path",
                    "example-domain.com/path",
                    "www.example-domain.com/relative/path",
                ]
            },
            {
                "name": "Process link given subdomain.example-domain.com",
                "processor_config": {
                    "subdomain": "subdomain",
                    "host": "example-domain.com"
                },
                "expected_url": "subdomain.example-domain.com",
                "page_loader_response": [
                    "<a href='https://www.example-domain.com/path'>this link should show in all_links</a>",
                    "<a href='example-domain.com/path'>this link should show in all_links</a>",
                    "<a href='other.example-domain.com/path'>this link should show in all_links</a>",
                    "<a href='subdomain.example-domain.com'>this link should show in both lists</a>",
                    "<a href='/relative/path'>this link should show in both lists as subdomain.example-domain.com/relative/path </a>"
                ],
                "expected_all_links": [
                    "https://www.example-domain.com/path",
                    "example-domain.com/path",
                    "other.example-domain.com/path",
                    "subdomain.example-domain.com",
                    "subdomain.example-domain.com/relative/path",
                ],
                "expected_local_links": [
                    "subdomain.example-domain.com",
                    "subdomain.example-domain.com/relative/path",
                ]
            },
        ]

        for test_case in test_cases:
            test_out.log_starting_test(test_case["name"])

            expected_url = test_case["expected_url"]
            page_loader_response = [line.encode(encoding="utf-8") for line in test_case["page_loader_response"]]
            expected_all_links = test_case["expected_all_links"]
            expected_local_links = test_case["expected_local_links"]

            processor = construct_link_processor(test_case["processor_config"])

            loader_instance: MockPageLoader = processor.page_loader_pool.get_instance_from_pool()
            loader_instance.set_return_content(page_loader_response)

            subdomain = processor.subdomain
            host = processor.host
            link = f"{subdomain}.{host}" if subdomain != "" else host

            all_links, local_links = await processor.process_link(link)
            called_link = loader_instance.called_link

            self.assertEqual(called_link, expected_url)
            self.assertEqual(all_links, expected_all_links)
            self.assertEqual(local_links, expected_local_links)
