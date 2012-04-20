import urlparse
from .base import Step

"""
Instead of handling 30X redirects as a HTTP case, we're handling them in the
response pipeline.
"""

class RobotCheck(Step):
    def __init__(self, settings, **kwargs):
        """Initialzation"""
        pass

    def process(self, task, callback=None, **kwargs):
        callback((Step.CONTINUE, task))
