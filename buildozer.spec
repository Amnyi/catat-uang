[app]

# Judul aplikasi
title = Catat Uang

# Nama package (tanpa spasi dan huruf besar)
package.name = catatuang

# Domain package (bebas)
package.domain = org.amny

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

# Semua ikon digambar lewat kode, jadi tidak perlu internet.
requirements = python3,kivy==2.3.0,sqlite3

orientation = portrait
fullscreen = 0
version = 1.0

# Database disimpan di penyimpanan privat aplikasi, jadi tidak perlu izin apa pun.
# (Kalau nanti butuh internet, hapus tanda # di bawah ini)
# android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True

android.allow_backup = True

# Kunci versi python-for-android yang stabil (memakai Python 3.11).
# Tanpa ini, buildozer memakai Python 3.14 dan Kivy 2.3.0 gagal dikompilasi.
p4a.branch = v2024.01.21

[buildozer]

# 2 = log lengkap untuk melihat proses
log_level = 2
warn_on_root = 1
