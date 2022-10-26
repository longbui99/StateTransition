from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StateTransition(models.Model):
    _name = "state.transition"
    _inherit = "state.transition.template"
    _description = "State Transition"
    _rec_name = 'name'

    tmpl_state_id = fields.Many2one("state.transition.template", string="Template", ondelete="cascade", required=True)

    def sync_tmpl_to_variant(self, values):
        self.ensure_one()
        self.update(values)

    @api.onchange("tmpl_state_id")
    def _onchange_tmpl_state_id(self):
        updating_values = self.prepare_sync_data()
        self.sync_tmpl_to_variant(updating_values)

    @api.model
    def create(self, values):
        if 'tmpl_state_id' in values:
            values.update(self.env['state.transition.template'].browse(values['tmpl_state_id']).prepare_sync_data())
        res = super().create(values)
        return res