// Set the require.js configuration for your application.
require.config({
    deps: ["main"],

    paths: {
        //
        // JavaScript folders
        /*
        text: "../vendor/text",
        */
        vendor: "../vendor",

        // Libraries
        jquery: "../vendor/jquery",
        underscore: "../vendor/underscore",
        backbone: "../vendor/backbone",
        handlebars: "../vendor/handlebars",
        distal: "../vendor/backbone.distal"
    },

    shim: {
        underscore: {
            exports: '_'
        },
        distal: {
            deps: ['backbone', 'handlebars'],
            exports: "Backbone.Distal"
        },
        handlebars: {
            exports: 'Handlebars'
        },
        "vendor/bootstrap": {
            deps: ['jquery']
        },
        "vendor/bootstrap-datepicker": {
            deps: ['vendor/bootstrap']
        },
        "vendor/jquery.tokeninput": {
            deps: ['jquery']
        },
        "vendor/jquery.drag-drop.plugin": {
            deps: ['jquery']
        },
        "vendor/backbone.collectioncache": {
            deps: ['backbone']
        },
        "vendor/backbone-filtered-collection": {
            deps: ['backbone']
        },
        "vendor/backbone.validation": {
            deps: ['backbone']
        },
        "vendor/backbone.queryparams": {
            deps: ['backbone']
        },
        "vendor/jquery.cookie": {
            deps: ['jquery']
        },
        "vendor/jquery.toggle.buttons": {
            deps: ['jquery']
        },
        "vendor/jquery.uploadify-3.1.min": {
            deps: ['jquery']
        },
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        }
    }
});
