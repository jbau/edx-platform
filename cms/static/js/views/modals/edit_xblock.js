define(["jquery", "underscore", "underscore.string", "gettext", "js/views/baseview", "js/views/feedback_notification",
        "js/views/xblock", "js/models/xblock_info", "js/views/metadata", "js/collections/metadata"],
    function($, _, str, gettext, BaseView, NotificationView,
             XBlockView, XBlockInfo, MetadataView, MetadataCollection) {
        var EditXBlockModal = BaseView.extend({
            events : {
                "click .action-save": "save",
                "click .action-cancel": "cancel",
                "click .action-modes a": "changeMode"
            },

            mode: 'editor-mode',

            options: $.extend({}, BaseView.prototype.options, {
                type: "prompt",
                closeIcon: false,
                icon: false
            }),

            constructor: function(options) {
                BaseView.prototype.constructor.apply(this, arguments);
                this.view = options.view;
            },

            initialize: function() {
                this.template = _.template($("#edit-xblock-modal-tpl").text());
            },

            render: function(options) {
                var self = this,
                    editorView,
                    xblockInfo = this.xblockInfo,
                    success = options ? options.success : null;
                this.$el.html(this.template());
                editorView = new XBlockView({
                    el: this.$('.xblock-editor'),
                    model: xblockInfo,
                    view: 'studio_view'
                });
                this.editorView = editorView;
                editorView.render({
                    success: function() {
                        if (success) {
                            success();
                        }
                        self.xblock = editorView.xblock;
                        self.createMetadataView();
                    }
                });
            },

            createMetadataView: function() {
                var metadataEditor = this.$('.metadata_edit'),
                    metadataData = metadataEditor.data('metadata'),
                    models = [],
                    key,
                    xblock = this.xblock;
                for (key in metadataData) {
                    if (metadataData.hasOwnProperty(key)) {
                        models.push(metadataData[key]);
                    }
                }
                this.settingsView = new MetadataView.Editor({
                    el: metadataEditor,
                    collection: new MetadataCollection(models)
                });
                if (xblock.setMetadataEditor) {
                    xblock.setMetadataEditor(this.settingsView);
                }
                if (this.hasDataEditor()) {
                    this.selectMode('editor');
                } else {
                    this.selectMode('settings');
                }
            },

            hasDataEditor: function() {
                return this.$('.wrapper-comp-editor').length > 0;
            },

            changeMode: function(event) {
                var parent = $(event.target.parentElement),
                    mode = parent.data('mode');
                event.preventDefault();
                this.selectMode(mode);
            },

            selectMode: function(mode) {
                var showEditor = mode === 'editor',
                    dataEditor,
                    editorModeButton,
                    settingsEditor,
                    settingsModeButton;
                dataEditor = this.$('.wrapper-comp-editor');
                settingsEditor = this.$('.wrapper-comp-settings');
                editorModeButton = this.$('.editor-button');
                settingsModeButton = this.$('.settings-button');
                if (showEditor) {
                    dataEditor.removeClass('is-inactive');
                    editorModeButton.addClass('is-set');
                    settingsEditor.removeClass('is-active');
                    settingsModeButton.removeClass('is-set');
                } else {
                    dataEditor.addClass('is-inactive');
                    editorModeButton.removeClass('is-set');
                    settingsEditor.addClass('is-active');
                    settingsModeButton.addClass('is-set');
                }
            },

            cancel: function(event) {
                event.preventDefault();
                this.hide();
            },

            edit: function(event, rootXBlockInfo, options) {
                event.preventDefault();
                this.xblockElement = this.findXBlockElement(event);
                this.xblockInfo = this.findXBlockInfo(this.xblockElement, rootXBlockInfo);
                this.editOptions = options;
                this.render({
                    success: _.bind(this.show, this)
                });
            },

            findXBlockElement: function(event) {
                return $(event.target).closest('[data-locator]');
            },

            findXBlockInfo: function(xblockElement, defaultXBlockInfo) {
                var xblockInfo = defaultXBlockInfo;
                if (xblockElement.length > 0) {
                    xblockInfo = new XBlockInfo({
                        'id': xblockElement.data('locator'),
                        'display-name': xblockElement.data('display-name'),
                        'category': xblockElement.data('category')
                    });
                }
                return xblockInfo;
            },

            show: function() {
                $('body').addClass('dialog-is-shown');
                this.$('.wrapper-dialog-edit-xblock').addClass('is-shown');
            },

            hide: function() {
                $('body').removeClass('dialog-is-shown');
                this.$('.wrapper-dialog-edit-xblock').removeClass('is-shown');
            },

            save: function(event) {
                var data,
                    saving,
                    self = this,
                    xblock = this.xblock,
                    xblockInfo = this.xblockInfo,
                    settingsView = this.settingsView;
                event.preventDefault();
                data = xblock.save();
                analytics.track("Saved Module", {
                    course: course_location_analytics,
                    id: xblock.id
                });
                data.metadata = _.extend(data.metadata || {}, settingsView.getModifiedMetadataValues());
                saving = new NotificationView.Mini({
                    title: gettext('Saving&hellip;')
                });
                saving.show();
                return xblockInfo.save(data).done(function() {
                    self.refreshChild({
                        success: function() {
                            var success = self.editOptions.success;
                            self.hide();
                            saving.hide();
                            if (success) {
                                success(self.xblockElement);
                            }
                        }
                    });
                });
            },

            refreshChild: function(options) {
                var xblockView = new XBlockView({
                    el: this.xblockElement,
                    model: this.xblockInfo,
                    view: this.view
                });
                xblockView.render(options);
            }
        });

        return EditXBlockModal;
    });
