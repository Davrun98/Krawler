import re

from instance_pooler.pooler import Pooler
from page_loader.loader import PageLoader

class LinkProcessorConfiguration:
    def __init__(self, page_loader_pool, subdomain, host):
        self.page_loader_pool = page_loader_pool
        self.subdomain = subdomain
        self.host = host


class LinkProcessor:
    def __init__(self, config: LinkProcessorConfiguration):
        self.page_loader_pool: Pooler = config.page_loader_pool
        self.page_loader_pool: Pooler = config.page_loader_pool
        self.subdomain: str = config.subdomain
        self.host: str = config.host

        # add www to expected host elements if subdomain is default ("")
        self.expected_host_elements = self.subdomain.split(".") if self.subdomain != "" else ["www"]
        self.expected_host_elements.extend(self.host.split("."))

    async def format_relative_link(self, parent_link:str, link: str) -> str:
        formatted_link = ""

        formatted_link += f"{self.subdomain}." if self.subdomain != "" else "www."

        formatted_link += self.host

        # remove domain from parent link
        parent_link_elements = parent_link.split("/", 1)  # domain.com, relative/path
        if len(parent_link_elements) > 1 and parent_link_elements[1] != "":
            parent_path = parent_link_elements[1]

            # remove filename from path
            path_elements = parent_path.split("/")
            if "." in path_elements[-1]:
                parent_path = "/".join(path_elements[:-1])

            # add path from parent link
            formatted_link += f"/{parent_path}"

        # add preceding slash if missing from relative path
        formatted_link += f"/{link}" if link[0] != "/" else f"{link}"

        return formatted_link


    async def evaluate_link(self, parent_link: str, link: str) -> tuple[bool, str]:
        """
        This element is insubstantial, due to the number of href variations.
        This won't work correctly for:
        - links using a different extension i.e. .com vs .co.uk (it's not a bug it's a feature)
        - links with the same subdomain more than once i.e. subdomain.subdomain.domain.ext will pass when expecting subdomain.domain.ext
        Alas, the technical challenge isn't about making the best URL parser... right?

        
        Args:
        link: (str) the link to evaluate

        Returns:
        valid, formatted_link: (tuple[bool, str])

        """

        # removes the scheme i.e. http/s
        scheme_separation = link.split("//", 1)
        remainder = scheme_separation[1] if len(scheme_separation) > 1 else scheme_separation[0]
        # removes the path. netloc will look like: `relativepathsection` or `sub.domains.domain.ext` or `domain.ext`
        netloc = remainder.split("/", 1)[0]
        # removes port numbers
        hostname = netloc.split(":", 1)[0]

        # capture links like `/relative/path` or `./relative/path` or `../relative/path` or `relative/path` 
        if netloc == "" or netloc == "." or netloc == ".." or "." not in netloc:
            return True, await self.format_relative_link(parent_link, link)

        # is third party link
        if self.host not in hostname:
            return False, ""
        
        # specified subdomain is absent
        if self.subdomain != "" and self.subdomain != "www" and self.subdomain not in hostname:
            return False, ""

        # incorrect subdomain is present
        domain_items = hostname.split(".")
        for item in domain_items:
            if item not in self.expected_host_elements:
                return False, ""

        return True, link
        

    async def process_link(self, link: str):
        # load page behind link
        loader: PageLoader = self.page_loader_pool.get_instance_from_pool()
        content = await loader.load_html(link)
        self.page_loader_pool.return_instance_to_pool(loader)

        # rip links - sets used to automate negation of duplicates
        all_links = set()
        local_links = set()
        for line in content:
            line = line.decode("utf-8")
            all_links.extend(re.findall(r'href=["|\'][^"\']*[^"|\']*["|\']', content))
        
        for found_link in all_links:
            is_valid, formatted_link = await self.evaluate_link(found_link)
            if is_valid:
                local_links.append(formatted_link)

        return all_links, local_links


def construct_link_processor(config: LinkProcessorConfiguration):
    return LinkProcessor(config)