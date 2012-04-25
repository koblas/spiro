function BackboneApp() {
    this.events = _.extend({}, Backbone.Events);
    this.fetchUserInfo();
    this.events.on('user', this.setUser, this);
}

BackboneApp.prototype = {
    start: function() {
        Backbone.history.start({ root: '/chatty' });
        this.events.trigger('start', '');
    },

    template: function(name, context) {
        return _.template( $("#" + name).html(), context);
    },

    processInfo: function(info) {
        this.socketURL = info.socketURL;
        this.events.trigger('connect-info', info);
    },

    setUser: function(user) {
        this.user = user;
    },

    fetchUserInfo: function() {
        // this.processInfo({ 'guid': 123 });
    }
}

app = new BackboneApp()
