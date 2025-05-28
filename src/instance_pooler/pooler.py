import math
from typing import Callable

class Pooler:
    def __init__(self, instance_constructor: Callable, instance_configuration: dict = {}):
        self.instance_constructor = instance_constructor
        self.instance_configuration = instance_configuration

        self.free_instances = []
        self.instance_count = 0

    """
    Fetches a free instance from the pool - new instances are created ad-hoc
    """
    def get_instance_from_pool(self):

        # if no free instances: create new instance - add to loaned pool - return
        if len(self.free_instances) == 0:
            instance = self.instance_constructor(self.instance_configuration)
            self.instance_count += 1
            return instance

        # otherwise, pull instance from pool
        return self.free_instances.pop()
    
    """
    Returns to instance to the free instance pool, triggers a pool reduction if more than half of the instances are free
    """
    def return_instance_to_pool(self, instance: object):
        self.free_instances.append(instance)

        if len(self.free_instances) > math.ceil(self.instance_count / 2):
            self.reduce_instance_pool()

    """
    Removes half of the free instances (roughly quarter of all instances)
    """
    def reduce_instance_pool(self):
        remove_count = math.floor(self.instance_count / 2)

        for _ in range(0,remove_count):
            self.free_instances.pop()
            

    