import urllib, urllib2, re, urlparse

__all__ = ['RobotParser']

def _unquote_path(path):
    # MK1996 says, 'If a %xx encoded octet is encountered it is unencoded 
    # prior to comparison, unless it is the "/" character, which has 
    # special meaning in a path.'
    path = re.sub("%2[fF]", "\n", path)
    path = urllib.unquote(path)
    return path.replace("\n", "%2F")

class RuleSet(object) :
    ALLOW    = 1
    DISALLOW = 0

    LABELS = { ALLOW : 'Allow: ', DISALLOW : 'Disallow: ' }

    def __init__(self) :
        self._rules      = []
        self._useragents = []
        self.crawl_delay = None

    def add_robot(self, robot) :
        if robot and len(robot) != 0 :
            self._useragents.append(robot)

    def add_allow(self, path) :
        self._add_rule(path, self.ALLOW)

    def add_disallow(self, path) :
        self._add_rule(path, self.DISALLOW)

    def not_empty(self) :
        return len(self._rules) != 0 and len(self._useragents) != 0

    def _add_rule(self, path, type) :
        if path and len(path) != 0 :
            if path.endswith('$') :
                appendix = '$'
                path = path[:-1]
            else :
                appendix = ""
            parts = path.split('*')
            pattern = ".*".join([re.escape(p) for p in parts]) + appendix

            regex = re.compile(pattern)
            #print (type, path, pattern)

            self._rules.append((type, path, regex))

    def match_useragent(self, ua) :
        for name in self._useragents :
            if name == '*' or name.lower() == ua.lower() :
                return True
        return False

    def is_allowed_path(self, url) :
        for type, path, regex in self._rules :
            if regex.match(url) :
                return type == self.ALLOW

        #print "NO rule for: ", url
        #print self
        return True

    def is_allowed(self, url) :
        scheme, host, path, parameters, query, fragment = urlparse.urlparse(url)
        url = urlparse.urlunparse(("", "", path, parameters, query, fragment))

        return self.is_allowed_path(_unquote_path(url)) 

    def __getitem__(self, url) :
        """Implement a matcher[url] = BOOLEAN checker"""
        return self.is_allowed(url)

    def __str__(self) :
        return "".join("User-agent: %s\n" % a for a in self._useragents) +  \
               "\n".join(["%s%s" % (self.LABELS[t], p) for t, p, r in self._rules])

class Matcher(object) :
    def __init__(self, rules, extra) :
        self.rules = rules
        self.extra = extra

    def is_allowed(self, url) :
        return self.rules.is_allowed(url) and self.extra.is_allowed(url)

    def is_allowed_path(self, url) :
        return self.rules.is_allowed_path(url) and self.extra.is_allowed_path(url)
        

class DefaultRuleSet(RuleSet) :
    def __init__(self) :
        super(DefaultRuleSet, self).__init__()

        self._useragents.append('*')

    def is_allowed(self, url) :
        return True

    def is_allowed_path(self, url) :
        return True


class RobotParser(object) :
    DEFAULT = DefaultRuleSet()

    def __init__(self, useragent = None, content = None, extra_rules=None) :
        self.source_url = None
        self.user_agent = useragent
        self._sitemap   = None
        self._rulesets  = []

        if extra_rules :
            self.extra_rules = RuleSet()
            for type, path in extra_rules :
                if type == 'allow' :
                    self.extra_rules.add_allow(path)
                else :
                    self.extra_rules.add_disallow(path)
        else :
            self.extra_rules = self.DEFAULT

        if content :    
            self.parse(content)

    def get_crawl_delay(self, user_agent = None) :
        """
        Get the crawl delay for the current user agent
        """
        
        ua = user_agent or self.user_agent or "*"

        for rules in self._rulesets :
            if rules.agentMatch(ua) :
                rules.crawl_delay
        return None

    def fetch(self, url) :
        """
        Attempts to fetch the URL requested which should refer to a 
        robots.txt file, e.g. http://example.com/robots.txt.
        """
        import urllib2

        self.source_url = url

        if self.user_agent :
            req = urllib2.Request(url, headers={ 'User-Agent' : self.user_agent })
        else :
            req = urllib2.Request(url)

        content = None

        fd = None
        try :
            fd = urllib2.urlopen(req)
            content = fd.read()
            expires = fd.info().getheader('Expires')
            content_type = fd.info().getheader('Content-Type')

            if hasattr(fd, "code") :
                self._response_code = fd.code
            else :
                self._response_code = 200
        except urllib2.URLError, e :
            if hasattr(e, 'code') :
                self._response_code = e.code
        if fd :
            fd.close()
                  

        # Handle expires, etc.

        if self._response_code >= 200 and self._response_code < 300 :
            pass
        elif self._response_code in (401, 403) :
            content = "User-agent: *\nDisallow: /\n"
        else :
            content = ""

        self.parse(content)

    def parse(self, content) :
        self._sitemap  = None
        self._rulesets = []

        #if not isinstance(content, unicode) :
            #content = unicode(content, 'ISO-8859-1')

        prev_was_useragent = False
        currule = None

        for line in content.split("\n") :
            line = line.strip()

            idx  = line.find('#')
            if idx >= 0 : 
                line = line[:idx]

            #
            #  Removed the '#' comment if it's empty, skip it.
            #
            if len(line) == 0 :
                continue

            p = line.split(':', 1)
            if len(p) == 1 :
                continue

            token = p[0].strip().lower()
            value = p[1].replace("\t", " ").strip()

            if token in ('useragent', 'user-agent') :
                if not prev_was_useragent :
                    currule = RuleSet()
                    self._rulesets.append(currule)
                currule.add_robot(value)
                prev_was_useragent = True
            else :
                if not currule :
                    currule = RuleSet()
                    self._rulesets.append(currule)
                prev_was_useragent = False

            if token in ('allow') :
                currule.add_allow(value)
            elif token in ('disallow') :
                currule.add_disallow(value)
            elif token in ('sitemap') :
                self._sitemap = value
            elif token in ('crawl-delay') :
                try :
                    currule.crawl_delay = float(value)
                except ValueError :
                    # Bad floating point number...
                    pass
            else :
                # Ignored this token...
                pass

    def is_allowed(self, useragent, url) :
        matcher = self.matcher(useragent)
        return matcher.is_allowed(url) and (not self.extra_rules or self.extra_rules.is_allowed(url))

    def matcher(self, useragent = None) :
        ua = useragent or self.user_agent or "*"
        for rule in self._rulesets :
            if rule.match_useragent(ua) :
                return Matcher(rule, self.extra_rules)
        return self.extra_rules

    def __str__(self) :
        s = "\n"
        if self._sitemap :
            s = "Sitemap: %s\n" % self._sitemap
        return s+'\n'.join([str(r) for r in self._rulesets])

    def __repr__(self) :
        import traceback
        traceback.pint_stack()
        print '<%s>' % (self.__class__.__name__)


def test1() :
    rp = RobotParser()
    rp.fetch('http://twitter.com/robots.txt')
    matcher = rp.matcher('*')

    turl = [
        '/',
        '/gelimon?max_id=5268363736&page=2&twttr=true',
        '/thisis_print_page.html',
        '/search?q=%22Happy+Halloween%22+OR+%23Halloween',
    ]

    for u in turl :
        print "%s => %s" % (u, matcher.is_allowed_path(u))


def test2() :
    content = """
User-Agent: Yahoo! Slurp
Allow: /public*/
Disallow: /*_print*.html
Disallow: /*?sessionid

User-Agent: *
Allow: /*
"""
    rp = RobotParser(useragent="Yahoo! Slurp", content=content, extra_rules=[
            ('disallow', '/tag/'),
        ])
    m = rp.matcher()
        
    turl = [
        '/',
        '/public/stuff/here',
        '/thisis_print_page.html',
        '/tag/gossip',
        '/tag/gossip',
    ]

    for u in turl :
        print "%s => %s" % (u, m.is_allowed(u))

if __name__ == '__main__' :
    test1()
    test2()
