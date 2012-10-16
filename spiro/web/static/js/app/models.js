define([
  // Libs
  "backbone",
  "underscore",
  "vendor/backbone.validation"
], function (Backbone, _) {
    //
    //  Tend to use things in a pretty standard for, might as well make a macro for
    //  the code, rather than doing a cut-n-paste on it every time.
    //
    function simpleMC(name, options) {
        options = options || {};

        var obj = {
                Model : Backbone.Model.extend({
                    url : function() {
                        return '/data/' + name + (this.isNew() ? '' : '/' + this.id);
                    },
                    validation: options.validation || {},
                    defaults: options.defaults
                })
        };

        obj.Collection = Backbone.Collection.extend({
                    url: '/data/' + name,

                    model: obj.Model,

                    cache: options.cache,
                })

        return obj;
    };


    //
    //
    //
    var Models = {
        Rules        : simpleMC('RobotRule'),
        Domains      : simpleMC('DomainConfiguration'),
        LogEntries   : simpleMC('LogEntries'),
        CrawlQueue   : simpleMC('Queue')
    };
    
    /*
    Models.CrawlerState = {
        Model : Backbone.Model.extend({
            url : function() {
                return '/data/CrawlerState/1';
            },
        })
    };
    */

    Models.Settings = {
        Model : Backbone.Model.extend({
            url : function() {
                return '/data/Settings/1';
            },
        })
    };

    Models.Rules.Collection.prototype.comparator = function(a, b) {
                var v = a.get('site').localeCompare(b.get('site'));
                if (v != 0) 
                    return v;
                v = a.get('path').localeCompare(b.get('path'));
                if (v != 0)
                    return v;
                return a.get('flag') - b.get('flag');
            };

    return Models;
});
