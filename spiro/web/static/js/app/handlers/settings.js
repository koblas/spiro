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
        templateName: 'settings_tmpl',

        events: {
        },

        initialize: function() {
            $('#leftbar .nav li').removeClass('active');
            $('#leftbar .nav #leftbar_settings').addClass('active');
        },
    });

    Handler.Controller = function () {
        var layout = app.layout.useLayout();

        layout.leftbar.show(new Backbone.Distal.View({ templateName: 'leftbar_tmpl' }));
        layout.main.show(new View());
    };

    app.router.route("settings", "settings", Handler.Controller);

    return Handler;
});
