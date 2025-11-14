from odoo import models, fields


class SttBilling(models.Model):
    _name = "lp.stt.billing"
    _description = "STT Billing Summary per Client"

    # Nanti kita isi field-nya di tahap berikut
    date = fields.Date(string="Date")
    client_code = fields.Char(string="Client Code")
    stt_count = fields.Integer(string="Total STT")
    debit = fields.Float(string="Debit")
    credit = fields.Float(string="Credit")
