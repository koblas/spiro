function Backsync() {
    var reconnect = true;
    var self = this;

    // _.bindAll(self, [self.onopen, self.onmessage, self.onclose]);
    _.bind(self.connect, self);
    _.bind(self.onopen, self);
    _.bind(self.onclose, self);
    _.bind(self.onmessage, self);

    self.connect();
}

_.extend(Backsync.prototype, Backbone.Events, {
    pending: [],

    connect: function() {
        this.sockjs = new SockJS('http://' + window.location.host + '/backsync');

        this.sockjs.onopen = this.onopen
        this.sockjs.onmessage = this.onmessage
        this.sockjs.onclose = this.onclose
        this.sockjs.sync = this;

        window.socket = this.sockjs;
    },

    addTx: function(id, success, error) {
        this.pending[id] = [error, success];
    },

    msgTx: function(id, msg) {
        var cb = this.pending[id];

        cb[0](msg);
    },

    onopen: function() {
        console.log('SockJS open');
        // this.sockjs.onmessage = this.onmessage;
    },

    onclose: function() {
        console.log('SockJS close');
        // setTimeout(this.sync.connect, 1000);
    },

    onmessage: function(e) {
        // console.log(e);
        var data = e.data;
        var self = this.sync;

        var cb = self.pending[data.id];
        if (cb) {
            delete self.pending[data.id];
            // console.log(data.data);
            if (data.data[0] && !!cb[0]) {
                cb[0](data.data[0]);
            } else if (!!cb[1]) {
                cb[1](data.data[1]);
            }
        } else {
            backsync.trigger(data.event, data.data);
        }
    }
});

var backsync = new Backsync(); 

Backbone.sync = function (method, model, options) {
    var getUrl = function (object) {
        if (!(object && object.url)) return null;
        return _.isFunction(object.url) ? object.url() : object.url;
    };

    var cmd = getUrl(model).split('/')
      , namespace = (cmd[0] !== '') ? cmd[0] : cmd[1]; // if leading slash, ignore

    var params = _.extend({
        req: namespace + ':' + method
    }, options);

    params.data = model.toJSON() || {};

    // If your socket.io connection exists on a different var, change here:
    var io = model.socket || window.socket || Backbone.socket;

    var id = Math.uuid();

    var payload = { id: id };

    if (method != 'read') {
        if (method == 'create' || method == 'update')
            method = 'upsert';
        payload.data = model.toJSON();
    }

    payload.event = namespace + ':' + method;
    
    var msg = JSON.stringify(payload);

    backsync.addTx(id, options.success, options.error);

    if (io.readyState != SockJS.OPEN) {
        io.addEventListener('open', function() {
            io.send(msg);
        });
    } else {
        io.send(msg);
    }
};

Backbone.Collection.prototype.syncBind = function(event, func, context) {
    var getUrl = function (object) {
        if (!(object && object.url)) return null;
        return _.isFunction(object.url) ? object.url() : object.url;
    };

    backsync.on(getUrl(this) + ':' + event, func, context);
}
