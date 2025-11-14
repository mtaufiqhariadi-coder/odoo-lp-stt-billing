import base64
import csv
from io import StringIO
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ImportSttWizard(models.TransientModel):
    _name = "lp.import.stt.wizard"
    _description = "Wizard untuk Import File STT (CSV)"

    data_file = fields.Binary(string="CSV File", required=True)
    filename = fields.Char(string="Filename")

    def _parse_date(self, s):
        # support beberapa format paling umum
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
        # kalau gagal, biarkan Odoo throw error saat create (atau return None)
        return None

    def action_import_stt(self):
        if not self.filename:
            raise ValidationError("Nama file tidak boleh kosong.")
        if not self.filename.lower().endswith(".csv"):
            raise ValidationError("Format file harus CSV.")

        # decode file bytes -> text
        try:
            file_content = base64.b64decode(self.data_file)
            text = file_content.decode("utf-8")
        except Exception as e:
            raise ValidationError(f"Gagal membaca file: {e}")

        reader = csv.DictReader(StringIO(text))
        aggregated = {}
        # key = (date_str, client_code)

        for i, row in enumerate(reader, start=1):
            # skip row kosong atau tidak lengkap sesuai soal
            date_raw = (row.get("date") or row.get("Date") or "").strip()
            client = (row.get("client_code") or row.get("client") or row.get("Client") or "").strip()
            client_type = (row.get("client_type") or row.get("clientType") or "").strip().upper()
            amount_raw = (row.get("amount") or row.get("Amount") or "0").strip()

            if not date_raw or not client or not client_type:
                # skip baris yang tidak lengkap (sama seperti soal)
                continue

            # try parse amount
            try:
                amount = float(amount_raw) if amount_raw else 0.0
            except Exception:
                amount = 0.0

            # konsistenkan tanggal untuk keying; kita simpan string YYYY-MM-DD
            parsed_date = self._parse_date(date_raw)
            if parsed_date:
                date_key = parsed_date.isoformat()
            else:
                # kalau format aneh, pakai apa adanya (tapi lebih aman pakai iso)
                date_key = date_raw

            key = (date_key, client)

            if key not in aggregated:
                aggregated[key] = {"stt_count": 0, "debit": 0.0, "credit": 0.0}

            aggregated[key]["stt_count"] += 1

            if client_type == "C":
                aggregated[key]["debit"] += amount
            elif client_type == "V":
                aggregated[key]["credit"] += amount
            else:
                # unknown type: skip contribution to debit/credit but still count STT
                continue

        Billing = self.env["lp.stt.billing"]

        for (date_str, client_code), vals in aggregated.items():
            # cari existing, kalau ada replace (menurut aturan STT2 override STT1)
            existing = Billing.search([("date", "=", date_str), ("client_code", "=", client_code)], limit=1)
            vals_write = {
                "stt_count": vals["stt_count"],
                "debit": vals["debit"],
                "credit": vals["credit"],
                "processed_from_file": self.filename,
            }
            if existing:
                existing.write(vals_write)
            else:
                Billing.create({
                    "date": date_str,
                    "client_code": client_code,
                    **vals_write
                })

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
