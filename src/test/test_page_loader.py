import unittest

from page_loader import loader
from test.common import test_out

"""
The test html link used here isn't guaranteed to work forever but it'll do for now - saves the effort of implementing a mockable http client pattern
https://www3.pioneer.com/argentina/PETWS/test.html
"""

_test_page_html_content = [
    "<html>\r\n",
    "<head>\r\n",
    "<title>This is a test static html page</title>\r\n",
    "</head>\r\n",
    "\r\n",
    "<body>\r\n",
    "<p>This is a test static html page for PETWS web site</p>\r\n",
    "</body>\r\n",
    "</html>",
]

class Testing(unittest.IsolatedAsyncioTestCase):
    async def test_load_html(self):
        test_out.log_starting_test_set("PageLoader - test load html")

        expected = [line.encode(encoding="utf-8") for line in _test_page_html_content]

        page_loader = loader.construct_page_loader()
        html_response = await page_loader.load_html("https://www3.pioneer.com/argentina/PETWS/test.html")

        self.assertEqual(expected, html_response)

    async def test_invalid_content_type(self):
        test_out.log_starting_test_set("PageLoader - test invalid content type")

        page_loader = loader.construct_page_loader()

        with self.assertRaises(loader.InvalidContentTypeException):
            await page_loader.load_html("https://github.com/favicon.ico")

    async def test_request_failed(self):
        test_out.log_starting_test_set("PageLoader - test request failed")

        page_loader = loader.construct_page_loader()

        with self.assertRaises(loader.RequestFailedException):
            await page_loader.load_html("https://fuery.co.uk/not/a/real/link")
            