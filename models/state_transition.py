from odoo import SUPERUSER_ID, models, fields, api, _
from odoo.exceptions import UserError


class StateTransition(models.Model):
    _name = "state.transition"
    _inherit = "state.transition.template"
    _description = "State Transition"
    _rec_name = 'name'

    tmpl_state_id = fields.Many2one("state.transition.template", string="Template", ondelete="cascade", required=True)

    _protect_fields = ["tmpl_state_id", "previous_code", "next_code", "model_id", "previous_code", "mode"]

    def sync_tmpl_to_variant(self, values):
        self.ensure_one()
        self.update(values)

    @api.onchange("tmpl_state_id")
    def _onchange_tmpl_state_id(self):
        updating_values = self.prepare_sync_data()
        self.sync_tmpl_to_variant(updating_values)

    @api.model
    def create(self, values):
        if self._context.get('stt_transition_kanban'):
            raise UserError(_("Cannot create/edit stage from Kanban View"))
        if 'tmpl_state_id' in values:
            values.update(self.env['state.transition.template'].browse(values['tmpl_state_id']).prepare_sync_data())
        res = super().create(values)
        return res

    def write(self, values):
        if self._context.get('stt_transition_kanban'):
            raise UserError(_("Cannot create/edit stage from Kanban View"))
        if any(project_field in values for project_field in self._protect_fields) and self.env.user.id != SUPERUSER_ID:
            if not all(self.mapped('tmpl_state_id.stt_transition_id.create_from_ui')):
                raise UserError(_("Cannot manually edit protect field on the static record!"))
        return super().write(values)

    def unlink(self):
        if self._context.get('stt_transition_kanban'):
            raise UserError(_("Cannot create/edit stage from Kanban View"))
        return super().unlink()
