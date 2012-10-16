define([
  // Global
  "app",

  // Libs
  "jquery",
  "underscore",
  "backbone",

  // Modules
  "models",

  // Extras
  "distal"
],

function (app, $, _, Backbone, Models) {
    var View = Backbone.Distal.View.extend({
        templateName: 'logline_tmpl',

        events: {
        },

        initialize: function() {
            this.timer = null;

            function fetch_data() {
                app.data.logentries.fetch({
                    data: {
                        token: app.data.logentries.token
                    },
                    add: true,
                    success: function(collection, response) {
                        var token = null;
                        _.each(response, function(item) {
                            token = token || item.token;
                        });
                        collection.token = token || collection.token;
                    }
                })
            };

            fetch_data();

            this.timer = setInterval(fetch_data, 5000);
        },

        onClose: function() {
            console.log("Close LogEntry view");
            if (this.timer)
                clearInterval(this.timer);
            this.timer = null;
        }
    });

    return View;
});
