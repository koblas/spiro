spiro
=====

Tornado Web Crawler

I really just wanted a "simple" web crawlwer, something that could fetch ... say 100,000 pages without breaking a sweat and save 
them to some storage (MongoDB or Riak).  This is what I threw together.

Usage
-----

Looks like a Tornado app.

    ./main.py --debug --port=8000

Point your web browser at it:

Reference Blog Posts
--------------------

   http://blog.semantics3.com/how-we-built-our-almost-distributed-web-crawler/
   http://www.michaelnielsen.org/ddi/how-to-crawl-a-quarter-billion-webpages-in-40-hours/

Other References
----------------

   http://dev.gbif.org/wiki/display/DEV/ZooKeeper+structure
   http://blog.marc-seeger.de/assets/papers/thesis_seeger-building_blocks_of_a_scalable_webcrawler.pdf

Techologies Used
----------------

* Tornado - Nonblocking Python Webserver - http://www.tornadoweb.org/
* Bootstrap - Pretty CSS - http://twitter.github.com/bootstrap/
* Backbone - JavaScript MVC - http://documentcloud.github.com/backbone/
* Distal - Backbone Views - https://github.com/koblas/distal
* Blinker - PubSub Signals - http://discorporate.us/projects/Blinker/
* MongoDB / Riak - KV NoSQL Database

