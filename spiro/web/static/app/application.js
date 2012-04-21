_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
};

var template = {
    form : _.template($('#form-template').html()),
    item : _.template($('#item-template').html()),
    event_item : _.template($('#event-item-template').html()),
};

var Spiro = {};

Spiro.App = Backbone.Router.extend({
    routes : {
        '' : 'index',
        '/' : 'index',
    },

    index : function() {
        var tasks  = new Spiro.Tasks();

        var form = new Spiro.TaskListForm(tasks);
        $('#TaskWrapper').append(form.el);

        var list = new Spiro.TaskList(tasks);
        $('#TaskWrapper').append(list.el);

        var events = new Spiro.LogEvents();
        var elist  = new Spiro.LogEventList({ collection: events, el: $('#LogEventWrapper') });

        tasks.fetch();
    }
});

Spiro.Task = Backbone.Model.extend({
    urlRoot : 'task',
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

Spiro.Tasks = Backbone.Collection.extend({
    model  : Spiro.Task,
    url    : 'tasks',
    socket : window.socket,
    initialize: function () {
        _.bindAll(this, 'serverCreate', 'collectionCleanup');
        this.ioBind('create', this.serverCreate, this);
    },
    serverCreate: function (data) {
        // make sure no duplicates, just in case
        var exists = this.get(data.id);
        if (!exists) {
            this.add(data);
        } else {
            data.fromServer = true;
            exists.set(data);
        }
    },
    collectionCleanup: function (callback) {
        this.ioUnbindAll();
        this.each(function (model) {
            model.modelCleanup();
        });
        return this;
    }
});

Spiro.TaskList = Backbone.View.extend({
    id: 'TaskList',
    initialize: function(tasks) {
        _.bindAll(this, 'render', 'addTask', 'removeTask');
    
        this.tasks = tasks;
    
        // this is called upon fetch
        this.tasks.bind('reset', this.render);
    
        // this is called when the collection adds a new task from the server
        this.tasks.bind('add', this.addTask);
    
        // this is called when the collection is told to remove a task
        this.tasks.bind('remove', this.removeTask);
    
        this.render();
    },
    render: function () {
        var self = this;

        this.tasks.each(function (task) {
            self.addTask(task);
        });

        return this;
    },
    addTask: function (task) {
        var tdv = new Spiro.TaskListItem(task);
        $(this.el).append(tdv.el);
    },
    removeTask: function (task) {
        var self = this
          , width = this.$('#' + task.id).outerWidth();
    
        self.$('#' + task.id).remove();
    }
});

Spiro.TaskListItem = Backbone.View.extend({
    className: 'task',
    events: {
        'click .complete': 'completeTask',
        'click .delete': 'deleteTask'
    },
    initialize: function (model) {
        _.bindAll(this, 'setStatus', 'completeTask', 'deleteTask');
        this.model = model;
        this.model.bind('change:completed', this.setStatus);
        this.render();
    },
    render: function () {
        $(this.el).html(template.item(this.model.toJSON()));
        $(this.el).attr('id', this.model.id);
        this.setStatus();
        return this;
    },
    setStatus: function () {
        var status = this.model.get('completed');
        if (status) {
            $(this.el).addClass('complete');
        } else {
            $(this.el).removeClass('complete');
        }
    },
    completeTask: function () {
        // here we toggle the completed flag. we do NOT
        // set status (update UI) as we are waiting for
        // the server to instruct us to do so.
        var status = this.model.get('completed');
        this.model.save({ completed: !!!status });
    },
    deleteTask: function () {
        // Silent is true so that we react to the server
        // broadcasting the remove event.
        this.model.destroy({ silent: true });
    }
});

Spiro.TaskListForm = Backbone.View.extend({
    id: 'TaskForm',
    events: {
        'click input#add': 'addTask'
    },
    initialize: function (tasks) {
        _.bindAll(this, 'addTask');
        this.tasks = tasks;
        this.render();
    },
    render: function () {
        $(this.el).html(template.form());
        return this;
    },
    addTask: function () {
        // We don't want ioBind events to occur as there is no id.
        // We extend Task#Model pattern, toggling our flag, then create
        // a new task from that.
        var Task = Spiro.Task.extend({ noIoBind: true });
        
        var attrs = {
            url: this.$('#TaskInput input[name="url"]').val(),
        };
    
        // reset the text box value
        this.$('#TaskInput input[name="url"]').val('');
    
        var _task = new Task(attrs);
        _task.save();

        return false;
    }
});

///
//
//
Spiro.Event = Backbone.Model.extend({
    urlRoot : 'event',
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

Spiro.Events = Backbone.Collection.extend({
    model  : Spiro.Event,
    url    : 'events',
    socket : window.socket,
    initialize: function () {
        _.bindAll(this, 'serverCreate', 'collectionCleanup');
        this.ioBind('create', this.serverCreate, this);
    },
    serverCreate: function (data) {
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

Spiro.EventList = Backbone.View.extend({
    id: 'EventList',
    initialize: function(events) {
        _.bindAll(this, 'render', 'addEvent', 'removeEvent');
    
        this.elist = events;
    
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
            self.addTask(event);
        });

        return this;
    },
    addEvent: function (event) {
        var tdv = new Spiro.EventListItem(event);
        $(this.el).append(tdv.el);
    },
    removeEvent: function (event) {
        this.$('#' + event.id).remove();
    }
});

Spiro.EventListItem = Backbone.View.extend({
    className: 'event',
    initialize: function (model) {
        // _.bindAll(this, 'setStatus', 'completeTask', 'deleteTask');
        this.model = model;
        // this.model.bind('change:completed', this.setStatus);
        this.render();
    },
    render: function () {
        console.log("NEW ITEM");
        $(this.el).html(template.event_item(this.model.toJSON()));
        $(this.el).attr('id', this.model.id);
        return this;
    }
});

$(document).ready(function () {
    window.app = new Spiro.App();
    Backbone.history.start();
});
