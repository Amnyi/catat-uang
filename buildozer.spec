[app]

# (str) Judul aplikasi kamu
title = Catat Uang

# (str) Nama package aplikasi (tanpa spasi dan huruf besar)
package.name = catatuang

# (str) Domain package (bebas)
package.domain = org.amny

# (list) Berkas source code yang akan dimasukkan ke dalam APK
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# (list) Modul/pustaka Python yang digunakan aplikasi kamu
requirements = python3,kivy,sqlite3

# (str) Orientasi layar (portrait = berdiri / vertikal)
orientation = portrait

# (bool) Indikator apakah aplikasi ini fullscreen atau tidak
fullscreen = 0

# (list) Izin akses HP (Android permissions)
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) Versi aplikasi
version = 1.0

# --- TAMBAHAN PENTING AGAR TIDAK ERROR ---
# (bool) Otomatis menyetujui lisensi Android SDK di server GitHub
android.accept_sdk_license = True

[buildozer]

# (int) Tingkat log/error (2 = debug lengkap untuk melihat proses)
log_level = 2

# (int) Target arsitektur (1 untuk arm64-v8a yang umum di HP modern)
android.archs = arm64-v8a
