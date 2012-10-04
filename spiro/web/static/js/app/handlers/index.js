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
        templateName: 'index_tmpl',

        events: {
            'submit #crawl'       : 'on_submit',
            'submit #crawl input' : 'on_submit',
            'click #crawl button' : 'on_submit'
        },

        initialize: function() {
            $('#leftbar .nav li').removeClass('active');
            $('#leftbar .nav #leftbar_home').addClass('active');
        },

        on_submit: function(evt) {
            var url = $('#crawl input').val();

            $.post('/data/Crawl', {
                url: url
            })

            $('#crawl input').val('');

            evt.stopPropagation();
            return false;
        }
    });

    Handler.Controller = function (id) {
        var layout = app.layout.useLayout();

        layout.leftbar.show(new Backbone.Distal.View({ templateName: 'leftbar_tmpl' }));
        layout.main.show(new View());
    };

    app.router.route("", "index", Handler.Controller);
    app.router.route("_=_", "index", function() {
        app.router.go('/');
    });

    return Handler;
});
