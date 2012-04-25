var User = Backbone.Model.extend({
     urlRoot : 'User',
     idAttribute: "guid",

     defaults: function() {
        return {
            screenName: 'You',
            guid: Math.uuid(),
            isMe: false
        };
     },

     toJSON: function() {
         return {
            cid: this.cid,
            guid: this.get('guid'),
            screenName: this.get('screenName'),
            isMe: this.get('isMe')
        };
    }
});

var Users = Backbone.Collection.extend({
    model: User,
    url: 'User',

    initialize: function (model) {
        this.syncBind('upsert', this.serverUpsert, this);
        this.syncBind('delete', this.serverDelete, this);
    },

    comparator: function(a, b) {
        if (a.isMe)
            return  1;
        if (b.isMe)
            return -1;
        var sa = a.get('screenName').toLowerCase(), sb = b.get('screenName').toLowerCase();
        if (sa > sb)
            return  1;
        if (sa < sb)
            return -1
        return 0;
    },

    serverUpsert: function(data) {
        // console.log("Server Upsert");
        var m = this.get(data.guid);
        if (m) {
            m.set(data);
        } else {
            this.add(data);
        }
    },

    serverDelete: function(data) {
        // console.log("Server Delete");
        var m = this.get(data.guid);
        if (m) 
            this.remove(m);
    },
});

var UserView = Backbone.View.extend({
    tagName: 'li',
    className: 'user',

    initialize: function(options) {
        this.isMe = options.isMe;
        this.model.view = this;
        this.model.on('change:screenName', this.setName, this);
    },

    setName: function() {
        var props = this.model.toJSON();
        props.isMe = this.isMe;
        this.$el.html(app.template('user', props));
    },

    render: function() {
        this.setName();
        return this.$el;
    },

    clickedUser: function(evt) {
        this.$el.addClass('active');
    },

    remove: function() {
        var self = this;
        this.$el.addClass('remove-red');
        this.$el.fadeOut(3000, function() {
            self.remove();
        });
    }
});

var UsersView = Backbone.View.extend({
    initialize: function(options) {
        this.user = options.user;
        this.collection.on('add', this.addUser, this);
        this.collection.on('remove', this.removeUser, this);
        this.collection.on('change', this.on_change, this);
        this.$numUsers = $("#num-users");
    },

    on_change: function() {
        this.render();
    },

    render: function() {
        var self = this;

        self.$el.find('.user').remove();        // FIXME - There should be a better jQuery way

        this.collection.each(function(item) {
            var view = new UserView({ model: item, isMe: self.user.id == item.id });
            self.$el.append(view.render());
        });
        this.$numUsers.text(this.collection.length);
    },

    addUser: function(user) {
        // var view = new UserView({ model: user });
        // this.$el.append(view.render());
        this.$numUsers.text(this.collection.length);
    },

    removeUser: function(user) {
        user.view.remove();
        this.$numUsers.text(this.collection.length);
    }
});

UserRouter = Backbone.Router.extend({
    routes: {
        "" : "allUsers",
        "users" : "allUsers",
        "users/:cid" : "userMessages"
    },

    initialize: function(options) {
        this.users = options.users
        this.$userList = $('#user-list');
        this.$allMessages = $(this.$userList.children()[1]);
    },

    allUsers: function() {
        this.removeActive();
        this.$allMessages.addClass('active');
        app.events.trigger('change-url', '');
    },

    userMessages: function(cid) {
        this.removeActive();
        this.users.getByCid(cid).view.clickedUser();
        app.events.trigger('change-url', this.users.getByCid(cid));
    },

    removeActive: function() {
        this.$userList.children().removeClass('active')
    }
});

function UserModule() {
    this.user = new User({ isMe: true });
    this.user.save();

    this.users = new Users();
    this.usersView = new UsersView({
        collection: this.users,
        el: '#user-list',
        user: this.user
    });

    this.users.add(this.user);
    this.users.fetch();

    this.router = new UserRouter({ users: this.users });

    this.addHandlers()
}

UserModule.prototype =  {
    addHandlers: function() {
        var self = this;

        app.events.on('connect-info', function(info) {
            self.user.id = info.id;
            self.publishUser();
        });

        app.events.on('screenName-entered', function(screenName) {
            self.user.set('screenName', screenName);
            self.publishUser();
        });

        app.events.on('new-user-connected', function(userInfo) {
            self.users.add(userInfo);
        });

        app.events.on('users-connected', function(usersConnected) {
            self.users.add(usersConnected);
        });

        app.events.on('users-disconnected', function(userInfo) {
            var model = this.users.get(userInfo.guid);
            self.users.remove(model);
        });
    },

    publishUser: function() {
        if (this.user.id != undefined && this.user.get('screenName') != 'You') {
            this.user.save();
            app.events.trigger('user', this.user);
        }
    }
};

userModule = new UserModule()
