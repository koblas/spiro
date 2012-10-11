from tornado.util import import_object
from .base import Step

store = None
def get_store(settings):
    global store
    if not store:
        cls = import_object(settings.STORE_CLASS)
        store = cls(settings=settings)
    return store

class StoreResponse(Step):
    """ Store a document into the storage """
    def __init__(self, settings, **kwargs):
        self.store = get_store(settings)

    def process(self, task, callback=None, **kwargs):
        self.store.update(task)
        callback((Step.CONTINUE, task))

class NeedFetch(Step):
    """ Check the store to see if we've recently fetched a document """
    def __init__(self, settings, **kwargs):
        self.store = get_store(settings)

    def process(self, task, callback=None, **kwargs):
        #if not task.force and self.store.has(task.url):
        #    action = Step.STOP
        #else:
        #    action = Step.CONTINUE

        callback((Step.CONTINUE, task))
