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
  "vendor/highcharts",
  "distal"
],

function (app, $, _, Backbone, Models) {
    var Handler = app.module();

    var View = Backbone.Distal.View.extend({
        templateName: 'stats_tmpl',

        events: {
        },

        initialize: function() {
            $('#leftbar .nav li').removeClass('active');
            $('#leftbar .nav #leftbar_stats').addClass('active');
            this.timer = null;

            this.pipe_stats = new Backbone.Collection()
        },

        post_render: function() {

            this.chart = new Highcharts.Chart({
                chart: {
                    renderTo: this.$('#statcontainer')[0],
                    animation: false,
                    type: 'line'
                },
                title: {
                    text: 'Page Processing'
                },
                xAxis: {
                    type: 'datetime',
                    minRange: 10 * 1000,
                    dateTimeLabelFormats: {
                        second: '%H:%M:%S',
                        minute: '%H:%M:00',
                    }
                },
                yAxis: [
                    {
                        title: { text: "Bytes" }
                    }, {
                        title: { text: "PPS" },
                        opposite: true
                    }
                ],
                series: [
                        {
                                name: 'Bytes per Second',
                                index: 0,
                                yAxis: 0,
                                pointInterval: 30 * 1000,
                                data: []
                        }, {
                                name: 'Pages per Second',
                                index: 1,
                                yAxis: 1,
                                pointInterval: 30 * 1000,
                                data: []
                        }
                ]
            });

            var self = this;

            function fetch_data() {
                $.ajax({
                    url: "/data/stats/pipeline",
                    dataType: 'json',
                    success: function(data) {
                        self.pipe_stats.reset(data);
                        self.pipe_stats.trigger('change');
                    }
                });

                $.ajax({
                    url: "/data/stats/",
                    dataType: 'json',
                    success: function(data) {
                        self.chart.series[0].setData(data.bps, false);
                        self.chart.series[1].setData(data.pps, true);
                    }
                });
            };

            fetch_data();
            
            this.timer = setInterval(fetch_data, 5000);
        },

        onClose: function() {
            if (this.timer) 
                clearInterval(this.timer);
            this.timer = null;
        }

    });

    Handler.Controller = function () {
        var layout = app.layout.useLayout();

        layout.leftbar.show(new Backbone.Distal.View({ templateName: 'leftbar_tmpl' }));
        layout.main.show(new View({ }));
    };

    app.router.route("stats", "stats", Handler.Controller);

    return Handler;
});
