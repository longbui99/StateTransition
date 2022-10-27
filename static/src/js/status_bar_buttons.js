/* global ace */
odoo.define('state_transition.status_bar_buttons', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var widgetRegistry = require('web.widget_registry');
    var Widget = require('web.Widget');

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
        _onBackToPreviousState: function () {
            if (this.transition?.previous) {
                let self = this;
                this._rpc({
                    model: self.transition.processing_model,
                    method: 'execute_action',
                    args: [self.transition.processing_id,
                        self._prepareStateMovingData({
                            'res_id': self.transition.previous.res_id,
                            'mode': 'previous'
                        })
                    ]
                }).then(result => {
                    self.reload()
                })
            }
        },
        _onNextState: function () {
            if (this.transition?.next) {
                let self = this;
                this._rpc({
                    model: self.transition.processing_model,
                    method: 'execute_action',
                    args: [self.transition.processing_id,
                        self._prepareStateMovingData({
                            'res_id': self.transition.next.res_id,
                            'mode': 'next'
                        })]
                }).then(result => {
                    self.reload()
                })
            }
        }

    });

    widgetRegistry.add('status_bar_buttons', StatusBarButtons);

    return StatusBarButtons;

});
