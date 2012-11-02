class Step(object):
    CONTINUE = 1
    STOP     = 2

    @property
    def name(self):
        return self.__class__.__name__

class LinkExtractorBase(object):
    def add_extracted_url(self, response, url):
        if not hasattr(response, 'spiro_extracted_urls'):
            response.spiro_extracted_urls = []
        response.spiro_extracted_urls.append(url)
