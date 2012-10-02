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
    var Handler = app.module();

    var View = Backbone.Distal.View.extend({
        templateName: 'queue_tmpl',

        events: {
        },

        queues: function() {
            return app.data.queue;
        }
    });

    Handler.Controller = function () {
        console.log("HERE");
        var layout = app.layout.useLayout();

        layout.leftbar.show(new Backbone.Distal.View({ templateName: 'leftbar_tmpl' }));
        layout.main.show(new View());
    };

    app.router.route("queue", "queue", Handler.Controller);

    return Handler;
});
