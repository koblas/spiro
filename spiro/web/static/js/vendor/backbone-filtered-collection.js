(function(_, Backbone) {
    var defaultFilter = function() {return true;};

    /**
    * This represents a filtered collection. You can either pass a filter or
    * invoke setFilter(filter) to give a filter. The filter is identical to
    * that which is used for _.select(array, filter)
    *
    * false filter indicates no filtering.
    *
    * do not modify this collection directly via #add/#remove, modify the
    * underlying origModel.
    */
    Backbone.FilteredCollection = Backbone.Collection.extend({
        collectionFilter: null,
        defaultFilter: defaultFilter,

        initialize: function(models, options) {
            if (models) 
                throw "models cannot be set directly, unfortunately first argument is the models.";

            this.__collection = options.collection;
            this.setFilter(options.collectionFilter);

            this.__collection.on("add",     this.on_add, this);
            this.__collection.on("remove",  this.on_remove, this);
            this.__collection.on("reset",   this.on_reset, this);
            this.__collection.on("change",  this.on_reset, this);
        },

        add: function() {
            throw "Do not invoke directly";
        },

        remove: function() {
            throw "Do not invoke directly";
        },

        reset: function() {
            throw "Do not invoke directly";
        },

        /*
         * Event handlers
         */
        on_add: function(model) {
            if (this.collectionFilter(model))
                Backbone.Collection.prototype.add.call(this, model);
        },

        on_remove: function(model) {
            Backbone.Collection.prototype.remove.call(this, model);
        },

        on_reset: function() {
            this.apply_filter();
        },

        /*
         *   Copied from Backbone.reset, needed to unwrap the 'add' call.
         */
        _backbone_reset: function(models, options) {
            models  || (models = []);
            options || (options = {});
            for (var i = 0, l = this.models.length; i < l; i++) {
                this._removeReference(this.models[i]);
            }
            this._reset();
            Backbone.Collection.prototype.add.call(this, models, _.extend({silent: true}, options));
            if (!options.silent) this.trigger('reset', this, options);
            return this;
        },

        apply_filter: function() {
            var models = this.__collection.filter(function (model) {
                return this.collectionFilter(model);
            }, this);

            this._backbone_reset(models);
        },

        setFilter: function(newFilter) {
            if (newFilter === false) { 
                // false = clear out filter
                newFilter = this.defaultFilter 
            }
            this.collectionFilter = newFilter || this.collectionFilter || this.defaultFilter;

            this.apply_filter();
        }
    });
})(_, Backbone);
