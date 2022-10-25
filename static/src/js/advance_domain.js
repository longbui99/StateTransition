/* global ace */
odoo.define('state_transition.basic_fields', function (require) {
    "use strict";
    const core = require('web.core');
    const config = require('web.config');
    const registry = require('web.field_registry');
    const Domain = require('web.Domain');
    const view_dialogs = require('web.view_dialogs');
    const DomainSelectorDialog = require('web.DomainSelectorDialog');
    const FieldDomain = require('web.basic_fields').FieldDomain;

    const _t = core._t;

    const FieldAdvanceDomain = FieldDomain.extend({
        //    Private Methods
        _formatDomainValue: function () {
            let value = this.value || '[]';
            value = value.replace('\"uid\"', this.record.context.uid);
            return value
        },
        _fetchCount(force = false) {
            if (!this._domainModel) {
                this._isValidForModel = true;
                this.nbRecords = 0;
                return Promise.resolve();
            }

            // do not re-fetch the count if nothing has changed
            const value = this._formatDomainValue(); // false stands for the empty domain
            const key = `${this._domainModel}/${value}`;
            if (!force && this.lastCountFetchKey === key) {
                return this.lastCountFetchProm;
            }
            this.lastCountFetchKey = key;

            this.nbRecords = null;

            const context = this.record.getContext({fieldName: this.name});
            this.lastCountFetchProm = new Promise((resolve) => {
                this._rpc({
                    model: this._domainModel,
                    method: 'search_count',
                    args: [Domain.prototype.stringToArray(value, this.record.evalContext)],
                    context: context
                }, {shadow: true}).then((nbRecords) => {
                    this._isValidForModel = true;
                    this.nbRecords = nbRecords;
                    resolve();
                }).guardedCatch((reason) => {
                    reason.event.preventDefault(); // prevent traceback (the search_count might be intended to break)
                    this._isValidForModel = false;
                    this.nbRecords = 0;
                    resolve();
                });
            });
            return this.lastCountFetchProm;
        },
        _onShowSelectionButtonClick: function (e) {
            e.preventDefault();
            new view_dialogs.SelectCreateDialog(this, {
                title: _t("Selected records"),
                res_model: this._domainModel,
                context: this.record.getContext({fieldName: this.name, viewType: this.viewType}),
                domain: this._formatDomainValue(),
                no_create: true,
                readonly: true,
                disable_multiple_selection: true,
            }).open();
        }
    });
    registry.add('advance_domain', FieldAdvanceDomain);

    return {
        FieldAdvanceDomain: FieldAdvanceDomain
    };

});
