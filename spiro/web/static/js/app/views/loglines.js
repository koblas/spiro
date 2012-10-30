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
                var collection = app.data.logentries;

                $.ajax("/data/LogEntries", {
                    async: true,
                    data: {
                        token: collection.token
                    },
                    dataType: 'json',
                    success: function(response, textStatus, xhr) {
                        collection.token = response.token || collection.token;

                        collection.add(response.items, { slient: true });

                        while (collection.length > 20) {
                            collection.shift({ silent: true });
                        }
                        collection.trigger('add');
                    }
                });
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
