#!/usr/bin/env python

import pymongo
from pyquery import PyQuery as pq
import re
import settings

def main():
    MATCH_RE = re.compile(r'^http://[^/]*pinterest\.com/[^/]+/$')
    connection = pymongo.Connection(settings.STORE_HOST, 27017)

    db = connection[settings.STORE_BUCKET]

    for doc in db.docs.find():
        #for link in doc.get('links', []):
        #    print link
        url = doc['url']
        if not MATCH_RE.search(url):
            continue
        q = pq(doc['body'])    
        subq = q('.info .content')
        if not subq:
            continue
        urls = [e.attrib.get('href') for e in subq("li a")]
        v = {
            'url' : url,
            'name': subq('h1').text().strip(),
            'urls': urls,
        }
        print v

if __name__ == '__main__':
    main()
