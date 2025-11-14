import base64
import csv
from io import StringIO
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ImportSttWizard(models.TransientModel):
    _name = "lp.import.stt.wizard"
    _description = "Wizard untuk import CSV STT"

    data_file = fields.Binary("CSV File", required=True)
    filename = fields.Char("Filename")

    def action_import_stt(self):
        # cek extension file untuk memastikan user tidak salah upload
        if not self.filename or not self.filename.lower().endswith(".csv"):
            raise ValidationError("File harus dalam format CSV.")

        # decode file biner jadi text.
        # pakai utf-8-sig supaya karakter BOM di awal file tidak mengganggu header.
        try:
            file_content = base64.b64decode(self.data_file)
            text = file_content.decode("utf-8-sig")
        except Exception:
            raise ValidationError("File tidak bisa dibaca. Pastikan format CSV valid.")

        # beberapa file CSV dari vendor bisa pakai delimiter yang berbeda.
        # di sini coba deteksi otomatis, kalau gagal default ke koma.
        try:
            sample = text.splitlines()[0]
            dialect = csv.Sniffer().sniff(sample)
            delimiter = dialect.delimiter
        except Exception:
            delimiter = ","

        reader = csv.DictReader(StringIO(text), delimiter=delimiter)

        aggregated = {}

        for row in reader:
            # beberapa file punya header/value dengan spasi atau karakter aneh.
            # disini dibersihkan supaya akses key lebih konsisten.
            clean = {
                (k.strip() if k else ""): (v.strip() if v else "")
                for k, v in row.items()
            }

            # ambil kolom sesuai format STT1/STT2
            date_raw = clean.get("date")
            client = clean.get("client_code")
            amount_raw = clean.get("amount")
            client_type = clean.get("client_type", "").upper()

            # baris dengan data kosong dilewati saja
            if not date_raw or not client or not client_type:
                continue

            # parsing tanggal: file dari soal ada yang pakai format mm/dd/yyyy
            # sementara ada file lain yang sudah yyyy-mm-dd.
            dt = None
            for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
                try:
                    dt = datetime.strptime(date_raw, fmt).date()
                    break
                except Exception:
                    pass

            if not dt:
                # fallback jika user upload format tanggal lain.
                raise ValidationError(f"Format tanggal tidak dikenali: {date_raw}")

            # parse amount. kalau gagal, nilai diset 0.
            try:
                amount = float(amount_raw)
            except Exception:
                amount = 0.0

            # key agregasi berdasarkan tanggal + client
            key = (dt.isoformat(), client)

            if key not in aggregated:
                aggregated[key] = {
                    "stt_count": 0,
                    "debit": 0.0,
                    "credit": 0.0,
                }

            aggregated[key]["stt_count"] += 1

            # aturan dari soal:
            # - client_type C masuk ke debit
            # - client_type V masuk ke credit
            if client_type == "C":
                aggregated[key]["debit"] += amount
            elif client_type == "V":
                aggregated[key]["credit"] += amount

        Billing = self.env["lp.stt.billing"]

        # simpan hasil agregasi ke model utama
        for (date_str, client_code), vals in aggregated.items():
            existing = Billing.search([
                ("date", "=", date_str),
                ("client_code", "=", client_code)
            ], limit=1)

            record_values = {
                "date": date_str,
                "client_code": client_code,
                "stt_count": vals["stt_count"],
                "debit": vals["debit"],
                "credit": vals["credit"],
                "processed_from_file": self.filename
            }

            # jika record sudah ada, replace nilai lama (logika override STT2)
            if existing:
                existing.write(record_values)
            else:
                Billing.create(record_values)

        # reload tampilan supaya user langsung melihat hasil import
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
