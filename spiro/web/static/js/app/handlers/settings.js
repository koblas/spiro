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
            'click form .btn' : 'on_submit',
        },

        initialize: function() {
            $('#leftbar .nav li').removeClass('active');
            $('#leftbar .nav #leftbar_settings').addClass('active');
        },

        on_submit: function(evt) {
            var vals = {};

            this.$el.find(':input').each(function (idx, el) {
                if (el.type == 'checkbox') 
                    vals[el.id] = el.checked;
                else
                    vals[el.id] = $(el).val();
            });

            this.model.save(vals);

            return false;
        }
    });

    Handler.Controller = function () {
        var layout = app.layout.useLayout();

        layout.leftbar.show(new Backbone.Distal.View({ templateName: 'leftbar_tmpl' }));
        layout.main.show(new View({ model: app.data.settings }));
    };

    app.router.route("settings", "settings", Handler.Controller);

    return Handler;
});
