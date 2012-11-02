
* Notification on settings changes
* Control how many locks a single instance can have and how it should release them
* Abstract the MongoDB portions that manage settings to a generic NoSQL store OHM model
* More dashboards
* Allow the upload of URL lists for crawling
* Better reporting on what's going on
* Support ARC file writer for crawled pages
* Distributed BloomFilter for crawled URLs?
* Pipeline performance page (how many times called, mean/average call time)
* Fabric deploy scripts for AWS
* Allow pipeline steps to add headers to the fetch e.g. If-Modified-Since and insure that the 
  correct actions happen if a 304 is returned.
