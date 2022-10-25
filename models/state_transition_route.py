from odoo import models, fields, api, _


class StateTransition(models.Model):
    _name = "state.transition.route"
    _description = "State Transition Route"
    _rec_name = "name"

    name = fields.Char(string="Name")
    stt_template_ids = fields.One2many("state.transition.template", "stt_transition_id", string="State Template")
    subscribe_model_ids = fields.Many2many("ir.model", string="Subscribe Model", ondelete="cascade")
