class RequestFailedException(Exception):
    pass


class InvalidContentTypeException(Exception):
    pass


class MockPageLoader:
    __return_content = []
    called_link = ""

    def set_return_content(self, page_content: list):
        # reset called link - just in case
        self.called_link = ""
        self.__return_content = page_content


    async def load_html(self, link) -> list:
        # sets the called link for validation
        self.called_link = link
        return self.__return_content
                

def construct_mock_page_loader(_) -> MockPageLoader:
    return MockPageLoader()