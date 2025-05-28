import unittest

from page_loader import loader

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
        expected = [line.encode(encoding="utf-8") for line in _test_page_html_content]

        page_loader = loader.construct_page_loader()
        html_response = await page_loader.load_html("https://www3.pioneer.com/argentina/PETWS/test.html")

        self.assertEqual(expected, html_response)

    async def test_invalid_content_type(self):
        page_loader = loader.construct_page_loader()

        with self.assertRaises(loader.InvalidContentTypeException):
            await page_loader.load_html("https://koroutine.tech/favicon.ico")

    async def test_request_failed(self):
        page_loader = loader.construct_page_loader()

        with self.assertRaises(loader.RequestFailedException):
            await page_loader.load_html("https://koroutine.tech/not/a/real/link")


if __name__ == '__main__':
    unittest.main()