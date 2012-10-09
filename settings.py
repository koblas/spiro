ROBOT_NAME = "spiro"
USER_AGENT = "Mozilla/5.0 (compatible; %s/0.1; +http://github.com/koblas/spiro)" % ROBOT_NAME

MAX_CLIENT = 10
MAX_SIMULTANEOUS_CONNECTIONS = 1
FOLLOW_REDIRECTS = False
MAX_REDIRECTS = 3
USE_GZIP = True

INTERNET = False

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

#DOMAIN_RESTRICT = (
#    'wink.com',
#    'twitter.com',
#    'geartracker.com',
#    'mylife.com',
#    'skitoy.com'
#)
