$(document).ready(function(){
    Backbone.emulateHTTP = true;

    var _sync = Backbone.sync;
    Backbone.sync = function (method, model, options) {

        // Add trailing slash to backbone model views
        var _url = _.isFunction(model.url) ? model.url() : model.url;
        _url += _url.charAt(_url.length - 1) == '/' ? '' : '/';

        options = _.extend(options, {
            url: _url
        });

        return _sync(method, model, options);
    };

    var _initialize = Backgrid.CellEditor.prototype.initialize;
    Backgrid.CellEditor.prototype.initialize = function(options){
        _initialize.call(this, options);
        this.formatter.options = {
            required: this.column.attributes.required,
            max_length: this.column.attributes.max_length
        };
    };

    Backgrid.NumberFormatter.prototype._toRaw = Backgrid.NumberFormatter.prototype.toRaw;
    Backgrid.NumberFormatter.prototype.toRaw = function(formattedData, model){
        if (this.options.required && formattedData==='') return;
        return Backgrid.NumberFormatter.prototype._toRaw.apply(this, arguments);
    };

    Backgrid.StringFormatter.prototype._toRaw = Backgrid.StringFormatter.prototype.toRaw;
    Backgrid.StringFormatter.prototype.toRaw = function(formattedData, model){
        if (this.options.required && formattedData==='') return;
        if (this.options.max_length && formattedData.length > this.options.max_length) return;
        return Backgrid.StringFormatter.prototype._toRaw.apply(this, arguments);
    };

    Backgrid.DatetimeFormatter.prototype._toRaw = Backgrid.DatetimeFormatter.prototype.toRaw;
    Backgrid.DatetimeFormatter.prototype.toRaw = function(formattedData, model){
        if (this.options.required && formattedData==='') return;
        return Backgrid.DatetimeFormatter.prototype._toRaw.apply(this, arguments);
    };

    var DatePickerCellEditor = Backgrid.DatePickerCellEditor = Backgrid.InputCellEditor.extend({
        postRender: function(model, column){
            DatePickerCellEditor.__super__.postRender.apply(this, arguments);
            this.$el.pikaday({
                onClose: function () {
                    var command = new Backgrid.Command({});
                    model.set(column.get("name"), this.getMoment().format('YYYY-MM-DD'));
                    model.trigger("backgrid:edited", model, column, command);
                }
            }).pikaday('show');
            return this;
        }
    });

    Backgrid.DateCell = Backgrid.DateCell.extend({
        editor: DatePickerCellEditor,
        exitEditMode: function () {
            this.$el.removeClass("error");
            if (this.currentEditor) {
                this.currentEditor.remove();
                this.stopListening(this.currentEditor);
                delete this.currentEditor;
            }
            this.$el.removeClass("editor");
            this.render();
        },
        enterEditMode: function(e){
            Backgrid.DateCell.__super__.enterEditMode.apply(this, arguments);

            e.stopPropagation();
        }
    });

    var Model = Backbone.Model.extend({
        initialize: function () {
            Backbone.Model.prototype.initialize.apply(this, arguments);
            this.on("change", function (model, options) {
                if (options && options.save === false) return;
                var model_attributes = Object.keys(model.attributes);
                if (_.difference(
                        window.required_attributes,
                        _.intersection(model_attributes, window.required_attributes)
                    ).length > 0) return;
                model.save(null, {
                    silent: true
                });
            });
        }
    });

    var ModelCollection = Backbone.Collection.extend({
        model: Model,
        initialize: function(options){
            this.model_class = options.model_class;
            this.url = '/model/' + this.model_class + '/';
        }
    });

    $('#models .edit').click(function(e){
        e.preventDefault();
        $("#grid").html();
        $("#control .create").hide();

        var model_class = $(this).data('model-class');

        window.modelCollection = new ModelCollection({
            model_class: model_class
        });

        $.get(
            '/model/'+model_class+'/info/',
            function (data){
                var columns = window.columns = _.map(data, function(item){
                    if (item.cell == 'integer'){
                        item.cell = Backgrid.IntegerCell.extend({
                            orderSeparator: ''
                        });
                    }
                    return item;
                });

                window.required_attributes = _.reduce(window.columns, function(memo, item){
                    if (item.required)
                        memo.push(item.name)
                    return memo;
                }, []);

                window.grid = new Backgrid.Grid({
                    columns: columns,
                    collection: window.modelCollection
                });

                $("#grid").html(grid.render().el);
                $("#control .create").show();

                modelCollection.fetch();
            }
        );

        return false;
    });
    $("#control .create").click(function(e){
        e.preventDefault();

        window.grid.insertRow([{}]);

        return false;
    });
});