import logging
import re

class PullThreadFilter(logging.Filter):
    def __init__(self):
        self.ignore = "GET \/thread\/\d+\S+ HTTP\/\S+ 200"

    def filter(self, record):
        return not re.search(self.ignore, record)
