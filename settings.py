USER_AGENT = "Mozilla/5.0 (compatible; spiro/0.1; +http://github.com/koblas/spiro)"

MAX_CLIENT = 10
MAX_SIMULTANEOUS_CONNECTIONS = 1
FOLLOW_REDIRECTS = False
MAX_REDIRECTS = 3
USE_GZIP = True

#
#  From when a URL is dequeued how we're going to process it.
#
PIPELINE = [
    'spiro.processor.store.NeedFetch',
    'spiro.processor.robots.RobotCheck',

    'spiro.processor.fetch.Fetch',

    'spiro.processor.redirect.RedirectExtraction',
    'spiro.processor.link_extractor.HtmlLinkExtractor',
    'spiro.processor.schedule.ScheduleUrls',
    'spiro.processor.store.StoreResponse',
]

#
#  Where we're storing objects
#
STORE_CLASS  = 'spiro.store.mongo.MongoStore'
STORE_BUCKET = 'spiro'
STORE_HOST   = 'localhost'
