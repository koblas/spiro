///
//
//
Spiro.LogEvent = Backbone.Model.extend({
    urlRoot : 'LogEvent',
    noIoBind: false,
    socket : window.socket,
    initialize: function() {
        _.bindAll(this, 'serverChange', 'serverDelete', 'modelCleanup');

        if (!this.noIoBind) {
            this.ioBind('update', this.serverChange, this);
            this.ioBind('delete', this.serverDelete, this);
        }
    },
    serverChange: function(data) {
        data.fromServer = true;

        this.set(data);
    },
    serverDelete: function (data) {
        if (this.collection) {
            this.collection.remove(this);
        } else {
            this.trigger('remove', this);
        }
        this.modelCleanup();
    },
    modelCleanup: function () {
        this.ioUnbindAll();
        return this;
    }
});

Spiro.LogEvents = Backbone.Collection.extend({
    model  : Spiro.LogEvent,
    url    : 'LogEvent_Collection',
    socket : window.socket,
    initialize: function () {
        _.bindAll(this, 'serverCreate', 'collectionCleanup');
        this.ioBind('create', this.serverCreate, this);
    },
    serverCreate: function (data) {
        if (this.models.length > 10)
            this.remove(this.models[0]);
        this.add(data);
    },
    collectionCleanup: function (callback) {
        this.ioUnbindAll();
        this.each(function (model) {
            model.modelCleanup();
        });
        return this;
    }
});

Spiro.LogEventList = Backbone.View.extend({
    // id: 'LogEventList',
    // tagName: 'ul',

    initialize: function() {
        _.bindAll(this, 'render', 'addEvent', 'removeEvent');

        // this.template = _.template($('#log_event-list-item-template').html());
    
        // this.elist = events;
        this.elist = this.collection;
    
        // this is called upon fetch
        this.elist.bind('reset', this.render);
    
        // this is called when the collection adds a new task from the server
        this.elist.bind('add', this.addEvent);
    
        // this is called when the collection is told to remove a task
        this.elist.bind('remove', this.removeEvent);
    
        this.render();
    },
    render: function () {
        var self = this;

        this.elist.each(function (event) {
            self.addEvent(event);
        });

        return this;
    },
    addEvent: function (event) {
        var item = new Spiro.LogEventListItem(event);
        this.$el.append(item.el);
    },
    removeEvent: function (event) {
        this.$('#' + event.id).remove();
    }
});

Spiro.LogEventListItem = Backbone.View.extend({
    className: 'event',
    initialize: function (model) {
        // _.bindAll(this, 'setStatus', 'completeTask', 'deleteTask');
        this.model = model;
        // this.model.bind('change:completed', this.setStatus);
        this.render();
    },
    render: function () {
        $(this.el).html(template.event_item(this.model.toJSON()));
        $(this.el).attr('id', this.model.id);
        return this;
    }
});
