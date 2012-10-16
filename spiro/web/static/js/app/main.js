require([
  // Global
  "app",

  // Libs
  "jquery",
  "underscore",
  "backbone",
  
  // Modules
  "models",

  // Extras
  "distal",
  "vendor/bootstrap",
  "vendor/bootstrap-datepicker",
  "vendor/backbone.queryparams",
  "vendor/jquery.tokeninput",
  "vendor/jquery.toggle.buttons",
  "vendor/jquery.cookie",
  // REVIST - "vendor/jquery.drag-drop.plugin",
  "vendor/backbone-filtered-collection",

  "handlers/index",
  "handlers/queue",
  "handlers/settings",
  "handlers/rules",
  "handlers/stats",
  "handlers/domains",
  "views/loglines",
  "views/crawl_state",
  // "handlers/collection_list",
  // "handlers/item_list",
  // "handlers/finish_reg",
  // "handlers/items",
  // "handlers/sharing",
  // "handlers/profile",
  // "handlers/locker",
  // "handlers/edit"
],

function (app, $, _, Backbone, Models) {
    //
    // This needs to be promoted to the "Window" level since we currently don't have
    // a way to register "namespaces" in Distal
    // 
    window.App = app;

    app.data = { };

    app.CrawlStateView = require("views/crawl_state");
    app.LogLineView    = require("views/loglines");

    // Defining the application router, you can attach sub routers here.
    var AppView = Backbone.Distal.LayoutView.extend({
        templateName:  'main_template',

        events: {
            'submit .navbar-search' : 'search' 
        },

        regions: {
                leftbar : '#leftbar', 
                main    : '#main',
                modal   : '#modal'
        },

        el: 'body',

        search: function(evt) {
            var $el = $(evt.target);

            var q = $el.find('input').val();
            $el.find('input').val('');

            app.router.go('search', q);

            return false;
        }
    });

    //
    //
    //
    app.layout.useLayout = function(name) {
            //
            // If already using this Layout, then don't re-inject into the DOM.
            if (app._layout) {
                console.log("Layout - Existing");
                return app._layout;
            }
            console.log("Layout - New");

            app._layout = new AppView();
            app._layout.render();

            return app._layout;
        };

    //
    //  Application Event handling....
    //

    app.events.on("startup", function() {
        // app.data.crawlerstate = new Models.CrawlerState.Model();
        // app.data.crawlerstate.fetch({ async: false });
        app.data.settings = new Models.Settings.Model();
        app.data.settings.fetch({ async: false });  // TODO - really async?

        app.data.queue      = new Models.CrawlQueue.Collection();
        app.data.logentries = new Models.LogEntries.Collection();
        app.data.rules      = new Models.Rules.Collection();
        app.data.domains    = new Models.Domains.Collection();

        app.data.rules.fetch();
        app.data.domains.fetch();
        
        app.data.logentries.token = '';
    });

    // Treat the jQuery ready function as the entry point to the application.
    // Inside this function, kick-off all initialization, everything up to this
    // point should be definitions.
    $(function() {
        app.events.trigger('startup');

        // Trigger the initial route and enable HTML5 History API support
        Backbone.history.start({ hashChange: true, pushState: true });
    });

    // All navigation that is relative should be passed through the navigate
    // method, to be processed by the router. If the link has a `data-bypass`
    // attribute, bypass the delegation completely.
    $(document).on("click", "a:not([data-bypass])", function(evt) {
        // Get the anchor href and protcol
        var href = $(this).attr("href");
        var protocol = this.protocol + "//";

        // Ensure the protocol is not part of URL, meaning it's relative.
        if (href && href.slice(0, protocol.length) !== protocol &&
            href.indexOf("javascript:") !== 0) {
          // Stop the default event to ensure the link will not cause a page
          // refresh.
          evt.preventDefault();

          // `Backbone.history.navigate` is sufficient for all Routers and will
          // trigger the correct events. The Router's internal `navigate` method
          // calls this anyways.
          Backbone.history.navigate(href, true);
        }
    });
});
