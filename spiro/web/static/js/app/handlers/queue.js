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

        initialize: function() {
            $('#leftbar .nav li').removeClass('active');
            $('#leftbar .nav #leftbar_queues').addClass('active');

            function fetch_data() {
                app.data.queue.fetch()
            };

            fetch_data();
            
            this.timer = setInterval(fetch_data, 5000);
        },

        onClose: function() {
            if (this.timer) 
                clearInterval(this.timer);
            this.timer = null;
        },

        queues: function() {
            return app.data.queue;
        }
    });

    Handler.Controller = function () {
        var layout = app.layout.useLayout();

        layout.leftbar.show(new Backbone.Distal.View({ templateName: 'leftbar_tmpl' }));
        layout.main.show(new View());
    };

    app.router.route("queue", "queue", Handler.Controller);

    return Handler;
});
