spiro
=====

Tornado Web Crawler

I really just wanted a "simple" web crawlwer, something that could fetch ... say 100,000 pages without breaking a sweat and save 
them to some storage (MongoDB or Riak).  This is what I threw together.

Usage
-----

Looks like a Tornado app.

    ./app.py --debug --port=8000

Point your web browser at it:


Techologies Used
----------------

* Tornado - Nonblocking Python Webserver - http://www.tornadoweb.org/
* Bootstrap - Pretty CSS - http://twitter.github.com/bootstrap/
* Backbone - JavaScript MVC - http://documentcloud.github.com/backbone/
* Backbone IO - Model/Collection Updates - http://alogicalparadox.com/backbone.iobind/
* Socket.IO - Transport - http://socket.io/
* Tornadio2 - Tornado connector to Socket.IO - https://github.com/MrJoes/tornadio2
* Blinker - PubSub Signals - http://discorporate.us/projects/Blinker/
* MongoDB / Riak - KV NoSQL Database
