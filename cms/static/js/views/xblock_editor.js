define(["jquery", "underscore", "js/views/xblock"],
    function ($, _, XBlockView) {

        var XBlockEditorView = XBlockView.extend({
            // takes XBlockInfo as a model

            options: $.extend({}, XBlockView.prototype.options, {
                view: 'studio_view'
            }),

            initialize: function() {
                XBlockView.prototype.initialize.call(this);
                this.view = this.options.view;
            }
        });

        return XBlockEditorView;
    }); // end define();
