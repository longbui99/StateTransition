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

    def _default_domain(self):
        return [('stt_transition_id.subscribe_model_ids.model', '=', self._name)]

    stt_transition_id = fields.Many2one("state.transition.template",
                                        string="State",
                                        domain=_default_domain,
                                        default=_default_stt_transition_id,
                                        group_expand='_read_group_stage_ids',
                                        copy=False)
    state = fields.Char(string="State", related="stt_transition_id.key", store=True, copy=False)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        field_domain = self._fields['stt_transition_id'].domain
        if callable(field_domain):
            field_domain = field_domain(self)
        stage_ids = stages.sudo()._search(field_domain, order=order)
        return stages.browse(stage_ids)

    def _update_state(self, state):
        self.ensure_one()
        transition_id = False
        for record in self.stt_transition_id.stt_transition_id.stt_template_ids:
            if record.key == state:
                transition_id = record
        self.stt_transition_id = transition_id
