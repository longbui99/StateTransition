from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StateTransition(models.Model):
    _name = "state.transition.route"
    _description = "State Transition Route"
    _rec_name = "name"

    name = fields.Char(string="Name")
    stt_template_ids = fields.One2many("state.transition.template", "stt_transition_id", string="State Template")
    subscribe_model_ids = fields.Many2many("ir.model", string="Subscribe Model", ondelete="cascade")
    create_from_ui = fields.Boolean(string="User Create?", default=True)

    def write(self, values):
        if 'create_from_ui' in values:
            return UserError(_("Cannot update record creating approach!"))
        return super().write(values)
    
    # @api.ondelete(at_uninstall=False)
    # def _unlink_route(self):
    #     if any(not route.create_from_ui for route in self):
    #         raise UserError(_("Cannot delete routes that aren't created manually"))
