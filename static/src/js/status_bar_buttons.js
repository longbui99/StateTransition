/* global ace */
odoo.define('state_transition.status_bar_buttons', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var widgetRegistry = require('web.widget_registry');
    var Widget = require('web.Widget');
    const Dialog = require('web.Dialog');

    var StatusBarButtons = Widget.extend({
        template: 'state_transition.TransitionButtonBox',
        tagName: 'button',
        events: {
            'click button.back-to-previous-state': '_onBackToPreviousState',
            'click button.next-state': '_onNextState',
        },
        init: function (parent, record, options = {}) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.recordData = record;
            this.attrs = options.attrs;
        },
        willStart: async function () {
            let self = this;
            let res = this._super.apply(this, arguments);
            if (this.attrs.transition) {
                let transition = this.recordData.data[this.attrs.transition];
                if (transition) {
                    let response = await this._rpc({
                        model: 'state.transition.template',
                        method: 'get_accessible_actions',
                        args: [transition.res_id, {
                            'active_model': self.recordData.model,
                            'active_id': self.recordData.res_id
                        }]
                    });
                    this.transition = response
                }
            }
            return res
        },
        reload: function () {
            let controller = this.findAncestor(function (obj) {
                return typeof obj.saveRecord === 'function'
            });
            controller.saveRecord(controller.handle, {
                stayInEdit: true,
            }).then(res => {
                controller.reload();
            })
        },
        _prepareStateMovingData: function (defaultData = {}) {
            let res = _.extend({
                'active_model': this.recordData.model,
                'active_id': this.recordData.res_id,
                'mode': 'previous',
                'field': this.attrs.transition
            }, defaultData);
            return res
        },
        _triggerAction: async function(mode, requestContent, force=false){
            let self = this;
            let requestBody = this._prepareStateMovingData({
                'res_id': requestContent.res_id,
                'mode': mode
            })
            if (requestContent?.confirm && !force){
                return Dialog.confirm(this, `${self.attrs.confirmation || 'Update to'} ${requestContent.title}`, 
                { confirm_callback: () => self._triggerAction(mode, requestContent, true) })
            } 
            this._rpc({
                model: self.transition.processing_model,
                method: 'execute_action',
                args: [self.transition.processing_id, requestBody]
            }).then(result => {
                self.reload()
            })
        },
        _onBackToPreviousState: function () {
            if (this.transition?.previous) {
                this._triggerAction("previous", this.transition.previous)
            }
        },
        _onNextState: async function () {
            if (this.transition?.next) {
                this._triggerAction("next", this.transition.next)
            }
        }
    });

    widgetRegistry.add('status_bar_buttons', StatusBarButtons);

    return StatusBarButtons;

});
