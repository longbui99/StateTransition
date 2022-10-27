import json

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND


class StateTransition(models.Model):
    _name = "state.transition.template"
    _description = "State Transition Template"
    _rec_name = "name"
    _order = "sequence asc, id desc"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", default=0)
    key = fields.Char(string="Key", required=True)
    reference = fields.Char(string="Reference")
    mode = fields.Selection([
        ("static_code", "Python Code"),
        ("server_action", "Server Action")
    ], string="Mode")
    stt_transition_id = fields.Many2one("state.transition.route", string="State Transition Route", ondelete="cascade")
    stt_transition_ids = fields.One2many("state.transition", "tmpl_state_id", string="State Variants")
    model_id = fields.Many2one("ir.model", string="Model", ondelete="cascade")
    model_model = fields.Char(related="model_id.model", store=True)
    # Previous State Domain
    previous_state_id = fields.Many2one("state.transition.template", string="Previous State")
    previous_state_user_domain = fields.Char(string="Applicable Users")
    previous_state_employee_domain = fields.Char(string="Applicable Employees")
    previous_group_domain = fields.Char(string="Applicable Groups")
    previous_model_domain = fields.Char(string="Applicable Records")
    previous_code = fields.Text(string="Code")
    # Next State Domain
    next_state_id = fields.Many2one("state.transition.template", string="Next State")
    next_state_user_domain = fields.Char(string="Applicable Users")
    next_state_employee_domain = fields.Char(string="Applicable Employees")
    next_group_domain = fields.Char(string="Applicable Groups")
    next_model_domain = fields.Char(string="Applicable Records")
    next_code = fields.Text(string="Code")
    start_ok = fields.Boolean(string="Start State")

    applicable_ok = fields.Boolean(string="Applicable State", default=False)

    _exclude_sync_fields = ["id", "stt_transition_id", "stt_transition_ids", "write_date", "create_date", "write_uid", "create_uid",
                            "__last_update"]


    _protect_fields = ["key", "start_ok"]

    def write(self, values):
        if any(project_field in values for project_field in self._protect_fields):
            if not all(self.mapped('stt_transition_id.create_from_ui')):
                raise ValidationError(_("Cannot manually edit protect field on the static record!"))
        return super().write(values)

    def prepare_sync_data(self):
        self.ensure_one()
        updating_fields = set(self._fields) - set(self._exclude_sync_fields)
        res = self._convert_to_write({name: self[name] for name in updating_fields})
        return res

    @api.constrains("mode")
    def _check_mode(self):
        for state in self.filtered(lambda stt: stt.mode == "static_code" and stt.model_id):
            if (state.previous_code and not hasattr(state.env[state.model_id.model], state.previous_code))\
             or (state.next_code and not hasattr(state.env[state.model_id.model], state.next_code)):
                raise ValidationError(_("""The method %s doesn't not exist in model %s (%s)!"""% (
                    state.key, state.model_id.name, state.model_id.model)))

    @api.model
    def get_state_by_key(self, key):
        return self.search([("key", "=", key), ("applicable_ok", "=", False)], limit=1)

    @api.depends("next_state_id", "previous_state_id")
    def _compute_applicable_ok(self):
        self.filtered(lambda state: (state.next_state_id or state.previous_state_id)).update({"applicable_ok": True})

    @api.model
    def _compile_user_domain(self, domain):
        index = 0
        while index < len(domain):
            if len(domain[index]) == 3:
                if domain[index][2] == "uid":
                    domain[index] = [domain[index][0], domain[index][1], self.env.user.id]
            index += 1
        return domain

    def action_create_variant(self):
        self.ensure_one()
        res = self._convert_to_write({name: self[name] for name in set(self._fields) - set(self._exclude_sync_fields)})
        res['tmpl_state_id'] = self.id
        state_transition_variant = self.env['state.transition'].create(res)
        return {
            "name": "Transition State Variant",
            "type": "ir.actions.act_window",
            "res_model": "state.transition",
            "view_mode": "form",
            "view_id": self.env.ref("state_transition.state_transition_form_view").id,
            "res_id": state_transition_variant.id,
        }

    def open_variant_ids(self):
        self.ensure_one()
        return {
            "name": "Transition State Variant",
            "type": "ir.actions.act_window",
            "res_model": "state.transition",
            "view_mode": "tree,form",
            "views": [(self.env.ref("state_transition.state_transition_template_tree_simplify_view").id, "tree"),
                      (self.env.ref("state_transition.state_transition_form_view").id, "form")],
            "domain": [("tmpl_state_id", "=", self.id)]
        }

    def _check_applicable_actions(self, user_domain, employee_domain, group_domain, record_domain, record=False):
        self.ensure_one()
        result = False
        if record and self._context.get("fit_model", False) and not result and isinstance(record_domain, list):
            record_domain = self._compile_user_domain(record_domain)
            record_domain = AND([record_domain, [("id", "=", record.id)]])
            result = bool(self.env[self.model_id.model].search(record_domain))
        if not result and isinstance(user_domain, list):
            user_domain = self._compile_user_domain(user_domain)
            user_domain = AND([user_domain, [("id", "=", self.env.user.id)]])
            result = bool(self.env["res.users"].search(user_domain, limit=1))
        if not result and isinstance(employee_domain, list):
            employee_domain = self._compile_user_domain(employee_domain)
            employee_domain = AND([employee_domain, [("user_id", "=", self.env.user.id), ("company_id", "=", self.env.company.id)]])
            result = bool(self.env["hr.employee"].search(employee_domain, limit=1))
        if not result and isinstance(group_domain, list):
            group_domain = self._compile_user_domain(group_domain)
            group_domain = AND([group_domain, [("users", "=", self.env.user.id)]])
            result = bool(self.env["res.groups"].search(group_domain))
        return result

    def get_accessible_actions(self, request):
        self.ensure_one()
        record = False
        if "active_model" in request and "active_id" in request:
            record = self.env[request["active_model"]].browse(request["active_id"]).exists()
        state = self.env["state.transition"].search([("tmpl_state_id", "=", self.id), ("model_id.model", "=", request["active_model"])], limit=1)
        state = state.with_context(fit_model=bool(state))
        processing_record = (state or self)
        response = {
            'processing_id': processing_record.id,
            'processing_model': processing_record._name
        }
        previous_state, next_state = self.previous_state_id, self.next_state_id
        if processing_record._check_applicable_actions(
                json.loads(state.previous_state_user_domain or self.previous_state_user_domain or "False"),
                json.loads(state.previous_state_employee_domain or self.previous_state_employee_domain or "False"),
                json.loads(state.previous_group_domain or self.previous_group_domain or "False"),
                json.loads(state.previous_model_domain or self.previous_model_domain or "False"),
                record
        ) and previous_state:
            response["previous"] = {
                "title": previous_state.display_name,
                "res_id": previous_state.id
            }
        if processing_record._check_applicable_actions(
                json.loads(state.next_state_user_domain or self.next_state_user_domain or "False"),
                json.loads(state.next_state_employee_domain or self.next_state_employee_domain or "False"),
                json.loads(state.next_group_domain or self.next_group_domain or "False"),
                json.loads(state.next_model_domain or self.next_model_domain or "False"),
                record
        ) and next_state:
            response["next"] = {
                "title": next_state.display_name,
                "res_id": next_state.id
            }
        return response

    def _execute_action(self, record, mode):
        self.ensure_one()
        assert mode in ("previous", "next"), "Mode %s is not supported" % mode
        executing_field = "%s_code" % mode
        if self.mode == "static_code" and self[executing_field]:
            if not hasattr(record, self[executing_field]):
                raise ValidationError(_("Cannot find method %s in model %s") % (self[executing_field], record._name))
            getattr(record.with_context(mode=mode), self[executing_field])()

    def execute_action(self, request):
        self.ensure_one()
        record = False
        if "active_model" in request and "active_id" in request:
            record = self.env[request["active_model"]].browse(request["active_id"]).exists()
        if record and "field" in request:
            if not hasattr(record, request["field"]):
                raise ValidationError(_("Cannot find field %s in model %s") % (request["field"], record._name))
            setattr(record, request["field"], request["res_id"])
        self._execute_action(record, request["mode"])
