from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SttBilling(models.Model):
    _name = "lp.stt.billing"
    _description = "STT Billing Summary per Client"
    _order = "date desc, client_code asc"

    # Saya tambahkan beberapa field untuk menyesuaikan kebutuhan laporan billing
    # khas logistic seperti di Lion Parcel.

    date = fields.Date(string="Date", required=True)
    client_code = fields.Char(string="Client Code", required=True)

    # Tambahan ini untuk menjelaskan billing ini asalnya dari file apa.
    # Di Lion Parcel kan data STT biasanya masuk bertahap harian.
    processed_from_file = fields.Char(
        string="Source File",
        help="Nama file CSV tempat data ini diambil. "
             "Sifatnya opsional, cuma untuk tracking saja."
    )

    stt_count = fields.Integer(string="Total STT", default=0)

    debit = fields.Float(string="Debit", default=0.0)
    credit = fields.Float(string="Credit", default=0.0)

    # Compute total amount hanya untuk convenience
    total_amount = fields.Float(
        string="Total Amount",
        compute="_compute_total_amount",
        store=True
    )

    @api.depends("debit", "credit")
    def _compute_total_amount(self):
        # Di sini sengaja saya pakai logika simpel:
        # total = debit - credit
        # Ini buat memudahkan pengecekan cepat di UI.
        for record in self:
            record.total_amount = record.debit - record.credit

    # Validasi sederhana: jangan sampai debit & credit dua-duanya ada
    @api.constrains("debit", "credit")
    def _check_debit_credit(self):
        for rec in self:
            if rec.debit > 0 and rec.credit > 0:
                raise ValidationError(
                    "Debit dan Credit tidak boleh terisi bersamaan."
                )

    # Validasi kedua: jumlah STT minimal 0
    @api.constrains("stt_count")
    def _check_stt_count(self):
        for rec in self:
            if rec.stt_count < 0:
                raise ValidationError("Jumlah STT tidak boleh negatif.")
