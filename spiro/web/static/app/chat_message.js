var Message = Backbone.Model.extend({
     urlRoot : 'ChatMessage',
     idAttribute: "guid",

     defaults: function() {
        return {
            color: 'black',
            username: 'anonymous',
            guid: Math.uuid(),
            isFromMe: false
        };
     }
});

var Messages = Backbone.Collection.extend({
    url    : 'ChatMessage',
    model  : Message,

    initialize: function (model) {
        this.syncBind('upsert', this.serverUpsert, this);
        this.syncBind('delete', this.serverDelete, this);
    },

    serverUpsert: function(data) {
        console.log("Server Upsert");
        var m = this.get(data.guid);
        if (m) {
            m.set(data);
        } else {
            this.add(data);
        }
    },

    serverDelete: function(data) {
        console.log("Server Delete");
        var m = this.get(data.guid);
        if (m) 
            this.remove(m);
    }
});

var MessageView = Backbone.View.extend({
    className: 'message-wrapper',

    initialize: function() {
        var self = this;

        this.model.view = this;

        app.events.on('user', function(user) { 
            console.log("USER", user);
            self.user = user; 
        });
        _.bindAll(this, 'render');
    },

    render: function() {
        this.$el.html(app.template('message', this.model.toJSON()));
        if (app.user && this.model.get('userId') == app.user.id)
            this.$el.addClass('is-from-me');
        return this.$el;
    },

    show: function() {
        this.$el.show();
    },

    hide: function() {
        this.$el.hide();
    }
});

var MessagesView = Backbone.View.extend({
    el: '#messages-inner',

    initialize: function() {
        this.collection = new Messages();
        this.collection.fetch();
        this.collection.on('reset', this.reset, this);
        this.collection.on('add', this.addMessage, this);
        this.eventHandlers();
    },

    eventHandlers: function() {
        var self = this;

        app.events.on('send-message', function(messagePacket) { 
            self.collection.create(messagePacket); 
        });

        app.events.on('receive-message', function(messagePacket) { 
            self.collection.add(messagePacket); 
        });

        app.events.on('change-url', function(user) { 
            self.filter(user);
        });
    },

    reset: function() {
        var self = this;
        this.$el.empty();
        this.collection.each(function(model) {
            var view = new MessageView({ model : model });
            self.$el.append(view.render());
        });
    },

    addMessage: function(message) {
        var view = new MessageView({model : message });
        this.$el.append(view.render());
        this.$el.animate({ scrollTop: 490 });
    },

    filter: function(user) {
        if (user == '') {
            this.collection.each(function(message) {
                message.view.show();
            });
        } else {
            var self = this;
            this.collection.each(function(message) {
                if (message.get('userId') != user.id) {
                    message.view.hide();
                } else {
                    message.view.show();
                }
            });
        }
    }
});

var SendMessageView = Backbone.View.extend({
    el: '#input',

    events: {
        'click button': 'sendMessage',
        "keypress input": "sendMessageWithEnter"
    },

    initialize: function() {
        var self = this;
        this.$input = this.$el.find('input');

        app.events.on('screenName-entered', function() { self.$input.focusin(); });
    },

    sendMessage: function(evt) {
        var message = this.$input.val()
        this.$input.val('')

        app.events.trigger('send-message', {
            userId: app.user.id,
            screenName: app.user.get('screenName'),
            time: (new Date()).getTime(),
            message: message,
            isFromMe: true
        });

        evt.preventDefault()
    },

    sendMessageWithEnter: function(evt) {
        if (evt.keyCode == 13)
            this.sendMessage(evt)
    }
});

function MessageModule() {
    this.messagesView = new MessagesView();
    this.sendMessageView = new SendMessageView();
}

messageModule = new MessageModule();
