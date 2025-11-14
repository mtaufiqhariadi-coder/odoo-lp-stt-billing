# Lion Parcel - STT Billing

Modul kecil untuk menyimpan hasil perhitungan billing STT. 
Modul ini saya buat sebagai bagian dari technical test, tetapi saya sesuaikan dengan 
use case yang lebih dekat ke dunia logistik (khususnya proses STT).

### Fitur utama:
- Model `lp.stt.billing` untuk menyimpan agregasi per tanggal dan client.
- Wizard untuk import CSV STT (mirip penggabungan STT1 & STT2).
- Data otomatis mengelompok berdasarkan:
  - tanggal
  - client_code
  - debit/credit dihitung dari client_type
- Jika file kedua mengandung data yang sama → otomatis overwrite (sesuai instruksi test).
- Tersedia menu billing dan menu import.
- Sudah mendukung pencarian berdasarkan tanggal, client, dan asal file.

Modul ini saya buat supaya orang lain yang baca bisa langsung paham alurnya,
dan mudah dites secara lokal.
