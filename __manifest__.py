{
    "name": "Lion Parcel - STT Billing",
    "version": "1.0.0",
    "summary": "Modul sederhana untuk menyimpan data billing hasil proses STT",
    "description": """
Modul ini dibuat sebagai latihan sekaligus adaptasi use case Lion Parcel.
Tujuannya untuk menyimpan hasil agregasi data STT (resi) per client dan per tanggal,
yang umumnya dihasilkan dari proses pipeline (misalnya Airflow).
""",
    "author": "M. Taufiq Hariadi",
    "category": "Operations",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/stt_billing_views.xml",
    ],
    "installable": True,
    "application": True,
}
