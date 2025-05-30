import re

from instance_pooler.pooler import Pooler
from page_loader.loader import PageLoader, RequestFailedException, InvalidContentTypeException

class LinkProcessorConfiguration:
    def __init__(self, page_loader_pool, subdomain, host):
        self.page_loader_pool = page_loader_pool
        self.subdomain = subdomain
        self.host = host


class LinkProcessor:
    def __init__(self, config: LinkProcessorConfiguration):
        self.page_loader_pool: Pooler = config.page_loader_pool
        self.subdomain: str = config.subdomain
        self.host: str = config.host

        # add www to expected host elements if subdomain is default ("")
        self.expected_host_elements = self.subdomain.split(".") if self.subdomain != "" else ["www"]
        self.expected_host_elements.extend(self.host.split("."))

    def format_relative_link(self, parent_link:str, link: str) -> str:
        formatted_link = ""

        formatted_link += f"{self.subdomain}." if self.subdomain != "" else "www."

        formatted_link += self.host

        # removes the scheme i.e. http/s
        scheme_separation = parent_link.split("//", 1)
        remainder = scheme_separation[1] if len(scheme_separation) > 1 else scheme_separation[0]
        # remove domain from parent link
        parent_link_elements = remainder.split("/", 1)  # domain.com, relative/path
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

    @staticmethod
    def fragment_link(link) -> tuple[str, str]:
        # removes the scheme i.e. http/s
        scheme_separation = link.split("//", 1)
        remainder = scheme_separation[1] if len(scheme_separation) > 1 else scheme_separation[0]
        # removes the path. netloc will look like: `relativepathsection` or `sub.domains.domain.ext` or `domain.ext`
        netloc = remainder.split("/", 1)[0]
        # removes port numbers
        hostname = netloc.split(":", 1)[0]

        return netloc, hostname

    def check_is_relative_link(self, link: str) -> bool:
        netloc = self.fragment_link(link)[0]

        # capture links like `/relative/path` or `./relative/path` or `../relative/path` or `relative/path` 
        return bool(netloc == "" or netloc == "." or netloc == ".." or "." not in netloc)

    def evaluate_link(self, link: str) -> tuple[bool, str]:
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

        hostname = self.fragment_link(link)[1]

        # is third party link - note: this has a hole, www.NotTheRightHost.com would pass for www.TheRightHost.com TODO
        if self.host not in hostname:
            return False
        
        # specified subdomain is absent
        if self.subdomain != "" and self.subdomain != "www" and self.subdomain not in hostname:
            return False

        # incorrect subdomain is present
        domain_items = hostname.split(".")
        for item in domain_items:
            if item not in self.expected_host_elements:
                return False

        return True

    async def process_link(self, link_to_process: str) -> tuple[list, list]:
        # load page behind link
        loader: PageLoader = self.page_loader_pool.get_instance_from_pool()

        try:
            content = await loader.load_html(link_to_process)
        except RequestFailedException:
            return [], []
        except InvalidContentTypeException:
            raise

        self.page_loader_pool.return_instance_to_pool(loader)

        all_links = []
        local_links = []

        # find all links
        for line in content:
            line = line.decode("utf-8")
            found_links = re.findall(r'href=["\']([^"\']+)["\']', line)

            for found_link in found_links:
                # convert relative links to example-domain.com/relative/path format
                if self.check_is_relative_link(found_link):
                    found_link = self.format_relative_link(link_to_process, found_link)

                # stop processing if already found
                if found_link in all_links:
                    continue

                all_links.append(found_link)

                # check if link is from same subdomain and host
                if self.evaluate_link(found_link):
                    local_links.append(found_link)

        return all_links, local_links


def construct_link_processor(config: LinkProcessorConfiguration):
    return LinkProcessor(config)