import asyncio

from instance_pooler.pooler import Pooler
from link_processor import processor
from page_loader import loader

class Orchestrator:
    def __init__(self, subdomain: str, host: str):
        page_loader_pool = Pooler(loader.construct_page_loader)
        link_processor_config = processor.LinkProcessorConfiguration(page_loader_pool, subdomain, host)
        
        self.link_processor_pool = Pooler(processor.construct_link_processor, link_processor_config)

        """
        registered_links structure:
        {
            "<link-name>": list[str](contained-links))
        }
        """
        self.registered_links = {}

    def run(self, base_link: str):
        # run
        asyncio.run(self.process_link(base_link))

        # output
        # json.dumps()

    async def process_link(self, link: str):
        link_processor_instance: processor.LinkProcessor = self.link_processor_pool.get_instance_from_pool()  
        all_links, local_links = link_processor_instance.process_link(link)
        self.link_processor_pool.return_instance_to_pool(link_processor_instance)

        # hellooooooo recursion - I should probably add a depth guard
        await self.register_links(link, all_links, local_links)

    async def register_links(self, link: str, contained_links: list, local_links: list):
        # register found details
        self.registered_links[link] = contained_links
        
        # check for any new unprocessed links
        to_recurse = []
        for new_link in local_links:
            if new_link not in self.registered_links:
                self.registered_links[new_link] = None  # this value is updated by a later call to this same function
                to_recurse.append(new_link)

        # recurse if necessary
        if len(to_recurse) > 0:
            tasks = [self.process_link(new_link) for new_link in to_recurse]
            await asyncio.gather(*tasks)


