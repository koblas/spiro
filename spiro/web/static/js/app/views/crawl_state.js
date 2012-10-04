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
        templateName: 'crawl_state_tmpl',

        events: {
        },

        post_render: function() {
            this.$('#crawler_running :checkbox').attr('checked', 
                                    app.data.settings.get('crawler_running'));

            this.$('#crawler_running').toggleButtons({
                onChange: function($el, state, e) {
                    app.data.settings.save({
                        crawler_running: state
                    });
                },

                style: {
                    enabled: "danger",
                    disabled: "info"
                }
            });
        }
    });

    return View;
});
