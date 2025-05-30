import aiohttp

_invalid_patterns = [".css", "cdn-cgi"]

class RequestFailedException(Exception):
    pass


class InvalidContentTypeException(Exception):
    pass


class PageLoader:
    @staticmethod
    def ensure_url_scheme(link: str) -> str:
        parts = link.split("//", 1)

        # if ['www.eg.com']  
        if len(parts) == 1:
            return f"http://{parts[0]}"
            
        # if ['', 'www.eg.com'] (aiohttp doesn't like //domain.com style blank schemes)
        if parts[0] == "": 
            return f"http://{parts[1]}"
        
        return link

    async def load_html(self, url) -> list:
        """
        load_html

        Args:
            url: the url to load

        Returns:
            list[bytes]: lines of html as bytes
        """
        
        url = self.ensure_url_scheme(url)

        # filter common invalid files
        for extension in _invalid_patterns:
            if extension in url:
                raise InvalidContentTypeException

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:

                if response.status < 200 or response.status > 299:
                    raise RequestFailedException

                if "text/html" not in response.headers.get("Content-Type"):
                    raise InvalidContentTypeException
                
                # pull complete lines from StreamReader before returning
                return [line async for line in response.content]
                

def construct_page_loader(_) -> PageLoader:
    return PageLoader()