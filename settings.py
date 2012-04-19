
USER_AGENT = "Mozilla/5.0 (compatible; spiro/0.1; +http://github.com/koblas/spiro)"

MAX_CLIENT = 10
MAX_SIMULTANEOUS_CONNECTIONS = 1
FOLLOW_REDIRECTS = False
MAX_REDIRECTS = 3
USE_GZIP = True


EXTRACT_PIPELINE = [
    'spiro.processor.redirect.RedirectExtraction',
    'spiro.processor.link_extractor.HtmlLinkExtractor',
    'spiro.processor.schedule.ScheduleUrls',
]
