import time
import socket
from collections import OrderedDict

import yaml


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)

    return yaml.load(stream, OrderedLoader)


def wait_for_port(host, port, timeout=2):
    start = time.time()
    end = start + timeout

    while True:
        try:
            s = socket.create_connection((host, port), timeout)
            s.close()
            return True
        except socket.error:
            pass

        time.sleep(.1)
        if time.time() > end:
            return False
