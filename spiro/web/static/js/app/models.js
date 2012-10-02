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
        LogEntries   : simpleMC('LogEntries'),
        CrawlQueue   : simpleMC('Queue')
    };
    
    Models.CrawlerState = {
        Model : Backbone.Model.extend({
            url : function() {
                return '/data/CrawlerState/1';
            },
        })
    };

    return Models;
});
