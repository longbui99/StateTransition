from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StateTransition(models.Model):
    _name = "state.transition"
    _inherit = "state.transition.template"
    _description = "State Transition"
    _rec_name = 'name'

    tmpl_state_id = fields.Many2one("state.transition.template", string="Template", ondelete="cascade")

    def prepare_sync_data(self):
        self.ensure_one()
        updating_fields = set(self._fields) - set(self._exclude_sync_fields)
        res = self._convert_to_write({name: self[name] for name in updating_fields})
        return res

    def sync_tmpl_to_variant(self, values):
        self.ensure_one()
        self.update(values)

    @api.onchange("tmpl_state_id")
    def _onchange_tmpl_state_id(self):
        updating_values = self.tmpl_state_id and self.tmpl_state_id.prepare_sync_data() or {}
        self.sync_tmpl_to_variant(updating_values)
