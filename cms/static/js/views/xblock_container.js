define(["jquery", "underscore", "js/views/xblock", "js/views/modals/edit_xblock"],
    function ($, _, XBlockView, EditXBlockModal) {

        var XBlockContainerView = XBlockView.extend({
            // takes XBlockInfo as a model

            options: $.extend({}, XBlockView.prototype.options, {
                view: 'container_preview'
            }),

            initialize: function() {
                this.noContentTemplate = _.template($("#no-content-tpl").text());
                XBlockView.prototype.initialize.call(this);
                this.view = this.options.view;
            },

            render: function(options) {
                XBlockView.prototype.render.call(this, options);
            },

            xblockReady: function(xblock) {
                XBlockView.prototype.xblockReady.call(this, xblock);
                if (this.hasChildXBlocks()) {
                    this.addButtonActions(this.$el);
                } else {
                    this.$el.html(this.noContentTemplate());
                }
            },

            hasChildXBlocks: function() {
                return this.$('.edit-button').length > 1;
            },

            addButtonActions: function(element) {
                var self = this;
                element.find('.edit-button').click(function(event) {
                    var modal = new EditXBlockModal({
                        el: $('.edit-xblock-modal'),
                        view: self.view
                    });
                    modal.edit(event, self.model,
                        {
                            success: function(element) {
                                self.addButtonActions(element);
                            }
                        });
                });
            }
        });

        return XBlockContainerView;
    }); // end define();
