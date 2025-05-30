from typing import Callable

class MockPooler:        
    def __init__(self, instance_constructor: Callable, instance_configuration: dict = {}):
        self.instance = instance_constructor(instance_configuration)

    def get_instance_from_pool(self):
        return self.instance
    
    def return_instance_to_pool(self, _):
        pass