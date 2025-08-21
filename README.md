# Library CIHEUL – Django Project

Perkenalkan saya Novrylianto Zundi Ramadhan selaku calon kandidat dari seleksi Ciheul Technologies.  
Project ini menggunakan Django 4.2.23 dan kompatibel dengan PostgreSQL 12.

## Screenshots
| Detail Buku All Tomorrow | Detail Buku Laskar Pelangi | Edit Buku | Edit Profil | Hapus Buku modal | Keyword NLTK modal | Login | Modal Preview Buku | Profil | Registrasi akun | Set Unset Favorit Buku | Tampilan Filter Favorit Buku | Tampilan Semua Buku | Tampilan awal belum login regristrasi | Upload Buku |
|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| <img src="./Screenshots/Detail Buku All Tomorrow.png" width="200"> | <img src="./Screenshots/Detail Buku Laskar Pelangi.png" width="200"> | <img src="./Screenshots/Edit Buku.png" width="200"> | <img src="./Screenshots/Edit Profil.png" width="200"> | <img src="./Screenshots/Hapus Buku modal.png" width="200"> | <img src="./Screenshots/Keyword NLTK modal.png" width="200"> | <img src="./Screenshots/Login.png" width="200"> | <img src="./Screenshots/Modal Preview Buku.png" width="200"> | <img src="./Screenshots/Profil.png" width="200"> | <img src="./Screenshots/Registrasi akun.png" width="200"> | <img src="./Screenshots/Set Unset Favorit Buku.png" width="200"> | <img src="./Screenshots/Tampilan Filter Favorit Buku.png" width="200"> | <img src="./Screenshots/Tampilan Semua Buku.png" width="200"> | <img src="./Screenshots/Tampilan awal belum login regristrasi.png" width="200"> | <img src="./Screenshots/Upload Buku.png" width="200"> |

## Petunjuk Instalasi

```cmd
:: 1. Buat dan aktifkan virtual environment
python -m venv venv_tesprogram
venv_tesprogram\Scripts\activate.bat

:: 2. Clone repository
git clone https://github.com/nofuri18/libraryciheulnov.git
cd library-ciheul

:: 3. Install dependencies
pip install -r requirements.txt

:: 4. Konfigurasi database
:: Ubah file :
source/app/conf/development/settings.py 
:: Saya menggunakan PostgreSQL 12

:: 5. Lakukan migrations
python source/manage.py migrate

:: 6. Jalankan server
python source/manage.py runserver
