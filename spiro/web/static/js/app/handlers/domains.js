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
        templateName: 'domains_tmpl',

        events: {
            'click form .btn' : 'on_submit',
            'submit form'     : 'on_submit',
            'click .delete_button' : 'delete_one'
        },

        initialize: function() {
            $('#leftbar .nav li').removeClass('active');
            $('#leftbar .nav #leftbar_domains').addClass('active');
        },

        on_submit: function(evt) {
            var vals = {};

            this.$el.find(':input').each(function (idx, el) {
                if (!el.id)
                    return;
                if (el.type == 'checkbox') {
                    vals[el.id] = el.checked;
                } else {
                    vals[el.id] = $(el).val();
                    $(el).val('')
                }
            });
            vals.flag = parseInt(vals.flag);

            var model = new Models.Domains.Model(vals);
            model.save()
            this.collection.add(model);

            return false;
        },

        delete_one: function(evt) {
            var data = $(evt.target).data('id');

            var model = this.collection.get(data);
            model.destroy();

            return false;
        }
    });

    Handler.Controller = function () {
        var layout = app.layout.useLayout();

        layout.leftbar.show(new Backbone.Distal.View({ templateName: 'leftbar_tmpl' }));
        layout.main.show(new View({ collection: app.data.domains }));
    };

    app.router.route("domains", "domains", Handler.Controller);

    return Handler;
});
