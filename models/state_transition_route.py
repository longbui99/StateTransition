from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


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
    
    @api.ondelete(at_uninstall=False)
    def _unlink_route(self):
        if any(not route.create_from_ui for route in self):
            raise UserError(_("Cannot delete routes that aren't created manually"))

    @api.constrains("subscribe_model_ids")
    def _check_subscribe_model_ids(self):
        models = self.mapped("subscribe_model_ids")
        if models:
            _sql_stmt_ = """
                SELECT ARRAY_AGG(ir_model_id) AS ids FROM (
                    SELECT COUNT(*), ir_model_id 
                    FROM ir_model_state_transition_route_rel
                    WHERE ir_model_id in %(ids)s
                    GROUP BY ir_model_id
                ) t WHERE t.count > 1
            """
            self.env.cr.execute(_sql_stmt_, {"ids": tuple(models.ids)})
            res = self.env.cr.dictfetchone().get("ids", [])
            if res:
                raise ValidationError(_("Specific model cannot subscribe to multiple route: \n\t- " + "\n\t- ".join(self.env['ir.model'].sudo().browse(res).mapped("display_name"))))