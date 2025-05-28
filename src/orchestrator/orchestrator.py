import asyncio
import json
import math
from datetime import datetime

from instance_pooler.pooler import Pooler
from link_processor import processor
from page_loader import loader


class Orchestrator:
    def __init__(self, subdomain: str, host: str, recursion_limit: int):
        page_loader_pool = Pooler(loader.construct_page_loader)
        link_processor_config = processor.LinkProcessorConfiguration(page_loader_pool, subdomain, host)
        
        self.link_processor_pool = Pooler(processor.construct_link_processor, link_processor_config)

        self.recursion_limit = recursion_limit if recursion_limit >= 0 else math.inf

        """
        registered_links structure:
        {
            "<link-name>": list[str](contained-links))
        }
        """
        self.registered_links = {}

        # links to skip - i.e. incorrect content-type
        self.skip_links = []


    def run(self, base_link: str):
        # add base link to registered links to stop it being re-run by the concurrency
        self.registered_links[base_link] = None
        # add base link without slash to skip it no file name is provided at the end of the path
        # this prevents duplication between `fuery.co.uk` and `fuery.co.uk/`
        if base_link[-1] == "/":
            self.skip_links.append(base_link[:-1])
        # run
        asyncio.run(self.process_link(base_link, 1))

        # output
        dt = datetime.now()
        filename = dt.strftime('krawl_%h-%m-%d_%H-%M-%S.json')

        with open(filename, 'w') as file:
            json.dump(self.registered_links, file, indent=2)


    def skip_link(self, link, recursion_limit_reached=False):
        if recursion_limit_reached and link in self.registered_links:
            self.registered_links[link] = "not processed - recursion limit reached"
        elif link in self.registered_links:
            self.skip_links.append(link)
            self.registered_links.pop(link)


    async def process_link(self, link: str, depth: int):
        # cancel processing if recursion depth is beyond limit
        if depth >= self.recursion_limit:
            self.skip_link(link, recursion_limit_reached=True)
            return

        link_processor_instance: processor.LinkProcessor = self.link_processor_pool.get_instance_from_pool()

        try:
            all_links, local_links = await link_processor_instance.process_link(link)
        except loader.InvalidContentTypeException:
            self.skip_link(link)
            self.link_processor_pool.return_instance_to_pool(link_processor_instance)
            return

        self.link_processor_pool.return_instance_to_pool(link_processor_instance)

        await self.register_links(link, all_links, local_links, depth)


    async def register_links(self, link: str, contained_links: list, local_links: list, depth: int):
        # register found details
        self.registered_links[link] = contained_links
        
        # check for any new unprocessed links
        to_recurse = []
        for new_link in local_links:
            if new_link not in self.registered_links and new_link not in self.skip_links:
                self.registered_links[new_link] = None  # this value is updated by a later call to this same function
                to_recurse.append(new_link)

        # recurse if necessary
        if len(to_recurse) > 0:
            depth += 1
            tasks = [self.process_link(new_link, depth) for new_link in to_recurse]
            await asyncio.gather(*tasks)


