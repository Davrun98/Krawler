import aiohttp

class RequestFailedException(Exception):
    pass


class InvalidContentTypeException(Exception):
    pass


class PageLoader:
    
    async def load_html(self, url) -> list:
        """
        load_html

        Args:
            url: the url to load

        Returns:
            list[bytes]: lines of html as bytes
        """
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:

                if response.status < 200 or response.status > 299:
                    raise RequestFailedException

                if response.headers.get("Content-Type") != "text/html":
                    raise InvalidContentTypeException
                
                # pull complete lines from StreamReader before returning
                return [line async for line in response.content]
                

def construct_page_loader() -> PageLoader:
    return PageLoader()