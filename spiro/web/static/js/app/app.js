define([
  // Libs
  "jquery",
  "underscore",
  "backbone",
  "distal"
],

function($, _, Backbone) {
    var tmplCache = {};

    Backbone.Distal.configure({
        path: {
            static: '/static'
        },

        fetch: function(name) {
            var el = $('#' + name);

            if (!tmplCache[name]) {
                if (el.length == 0) {
                    var url = this.path.static + '/tmpl/' + name + '.html';

                    $.ajax({ url: url, async: false }).then(function(contents) {
                        tmplCache[name] = contents;
                    });
                } else {
                    tmplCache[name] = el.html();
                }
            }

            return tmplCache[name];
        }
    });

    var modules = {};

    var app = {
        // Create a custom object with a nested Views object
        module: function(additionalProps) {
            return _.extend({ View: {} }, additionalProps);
        },

        // Keep active application instances namespaced under an app object.
        events: _.extend({}, Backbone.Events),

        layout: {}
    };

    app.router = new (Backbone.Router.extend({
                        app: app,
                        go: function() {
                            return this.navigate(_.toArray(arguments).join("/"), true);
                        }
                    }));

    return app;
});
