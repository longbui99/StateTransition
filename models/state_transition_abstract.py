from odoo import models, fields, api, _


class StateTransitionAbstract(models.AbstractModel):
    _name = "state.transition.abstract"
    _description = "State Transition Abstract"

    @api.model
    def _default_stt_transition_id(self):
        return self.env['state.transition.template'].search([
            ('stt_transition_id.subscribe_model_ids.model', '=', self._name),
            ('start_ok', '=', True)
        ], limit=1).id

    stt_transition_id = fields.Many2one("state.transition.template", 
        string="State", 
        domain=[('stt_transition_id.subscribe_model_ids.model', '=', _name)],
        default=_default_stt_transition_id)

