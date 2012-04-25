var LoadView = Backbone.View.extend({
    className: 'modal',

    events: {
        "keypress input": "doneWithEnter",
        "click #done":"done"
    },

    initialize: function() {
        var self = this;

        this.closedWindow = false;

        this.$el.on('hidden', function(evt) {
            self.done(evt);
        });
    },

    done: function(evt) {
        if (this.closedWindow) 
            return;
        this.closedWindow = true;
        var enteredName = this.$el.find('input').val();
        var anonName = 'Anonymous' + String((new Date()).getTime() % 1000);

        if (enteredName == '') 
            enteredName = anonName;
        
        app.events.trigger('screenName-entered', enteredName);
        this.$el.modal('hide');
        evt.preventDefault();
    },

    doneWithEnter: function(evt) {
        if (evt.keyCode == 13)
            this.done(evt);
    },

    render: function() {
        var tmpl = app.template('modal', {});

        this.$el.html(tmpl);
        this.$el.modal({ backdrop: true });
        this.$el.find('input').focus();
    }
});

function LoadModule() {
    this.loadView = new LoadView();
    this.eventHandlers();
}

LoadModule.prototype.eventHandlers = function() {
    var self = this;
    app.events.on('start', function() { self.loadView.render(); });
};

new LoadModule()
