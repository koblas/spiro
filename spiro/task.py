import urlparse

class Task(object):
    def __init__(self, url=None):
        self.url      = url
        self.links    = []
        self.request  = None
        self.response = None
        self.content_type = None
        self._parsed  = None

    @property
    def parsed_url(self):
        if not self._parsed:
            self._parsed = urlparse.urlparse(self.url)
        return self._parsed

    @property
    def url_scheme(self):
        return self.parsed_url.scheme

    @property
    def url_path(self):
        p = self.parsed_url.path
        if p == '':
            return '/'
        return p

    @property
    def url_host(self):
        p = self.parsed_url

        try:
            host = p.netloc
            host, port = host.split(':')
            return host
        except:
            return p.netloc

    def content_from_response(self):
        """
        Determine the content encoding based on the `Content-Type` Header.
        """
        if not self.response:
            return None

        self.content_charset = ""
            
        self.content_type = self.response.headers.get('content-type', 'text/plain')

        if not self.response.body:
            return None

        if self.content_type.find(';') == -1:
            self.content_charset = ''
        else:
            parts = self.content_type.split(';')
            self.content_type = parts[0]
            for part in parts[1:]:
                part = part.strip()
                if part.lower().startswith('charset'):
                    self.content_charset = part.split('=')[1].strip()
                    break

        if not self.content_charset:
            # TODO - No charset in header, look in the body for meta or XML header
            pass

        if not self.content_charset:
            self.content_charset = 'utf-8'

        return self.response.body.decode(self.content_charset, errors='ignore')

    def __repr__(self):
        return "<Task %s>" % self.url
