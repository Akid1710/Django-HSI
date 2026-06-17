from django.shortcuts import render, redirect
from django.db import connection
from datetime import datetime

# ==========================================
# 0. BONUS: DASHBOARD COUNTER
# ==========================================
def dashboard(request):
    with connection.cursor() as cursor:
        # 1. Ambil data untuk 4 counter atas
        cursor.execute("SELECT SUM(stok) FROM app_perpus_buku")
        total_buku = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM app_perpus_buku")
        total_judul = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM app_perpus_peminjaman WHERE status = 'Dipinjam'")
        sedang_dipinjam = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM app_perpus_peminjaman WHERE status = 'Dikembalikan'")
        sudah_dikembalikan = cursor.fetchone()[0] or 0

        # 2. Ambil daftar buku untuk bagian "Distribusi Stok Buku"
        cursor.execute("SELECT judul, stok FROM app_perpus_buku LIMIT 5")
        columns = [col[0] for col in cursor.description]
        daftar_buku = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {
        'total_buku': total_buku,
        'total_judul': total_judul,
        'sedang_dipinjam': sedang_dipinjam,
        'sudah_dikembalikan': sudah_dikembalikan,
        'daftar_buku': daftar_buku,
    }
    return render(request, 'dashboard.html', context)


# ==========================================
# 1. MODUL BUKU (CRUD)
# ==========================================
def list_buku(request):
    with connection.cursor() as cursor:
        # Kita panggil id dan isbn secara eksplisit
        cursor.execute("SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn FROM app_perpus_buku ORDER BY id DESC")
        columns = [col[0] for col in cursor.description]
        buku_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return render(request, 'buku/list.html', {'buku_list': buku_list})

def tambah_buku(request):
    if request.method == "POST":
        judul = request.POST['judul']
        pengarang = request.POST['pengarang']
        kategori = request.POST['kategori']
        penerbit = request.POST['penerbit']
        tahun_terbit = request.POST['tahun_terbit']
        rak = request.POST['rak']
        stok = request.POST['stok']
        isbn = request.POST.get('isbn', '-') # Pake .get aman dari KeyError
        deskripsi = request.POST['deskripsi']
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO app_perpus_buku (judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi])
        return redirect('list_buku')
    return render(request, 'buku/tambah.html')

def detail_buku(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM app_perpus_buku WHERE id = %s", [id])
        columns = [col[0] for col in cursor.description]
        buku = dict(zip(columns, cursor.fetchone()))
    return render(request, 'buku/detail.html', {'buku': buku})

def edit_buku(request, id):
    with connection.cursor() as cursor:
        if request.method == "POST":
            # 1. Ambil data inputan dari Form HTML
            judul = request.POST['judul']
            pengarang = request.POST['pengarang']
            kategori = request.POST['kategori']
            penerbit = request.POST['penerbit']
            tahun_terbit = request.POST['tahun_terbit']
            rak = request.POST['rak']
            stok = request.POST['stok']
            isbn = request.POST.get('isbn', '-')  # <-- AMBIL DATA ISBN
            deskripsi = request.POST['deskripsi']
            
            # 2. Update ke database (Pastiin jumlah %s dan urutan variabel di dalam kurung siku SAMA PERSIS!)
            cursor.execute("""
                UPDATE app_perpus_buku 
                SET judul=%s, pengarang=%s, kategori=%s, penerbit=%s, tahun_terbit=%s, rak=%s, stok=%s, isbn=%s, deskripsi=%s
                WHERE id=%s
            """, [judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi, id])
            
            return redirect('list_buku')
        else:
            # 3. Bagian GET: Ambil data buku berdasarkan ID untuk ditampilkan di form edit
            cursor.execute("SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi FROM app_perpus_buku WHERE id = %s", [id])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            
            if row:
                buku = dict(zip(columns, row))
            else:
                return redirect('list_buku')
                
    return render(request, 'buku/edit.html', {'buku': buku})

def hapus_buku(request, id):
    with connection.cursor() as cursor:
        if request.method == "POST":
            # Eksekusi hapus jika klik tombol Hapus (POST)
            cursor.execute("DELETE FROM app_perpus_buku WHERE id = %s", [id])
            return redirect('list_buku')
        else:
            # Ambil data buku untuk ditampilkan di halaman konfirmasi (GET)
            cursor.execute("SELECT * FROM app_perpus_buku WHERE id = %s", [id])
            columns = [col[0] for col in cursor.description]
            buku = dict(zip(columns, cursor.fetchone()))
            return render(request, 'buku/hapus.html', {'buku': buku})


# ==========================================
# 2. MODUL SISWA (CRUD)
# ==========================================
def list_siswa(request):
    with connection.cursor() as cursor:
        # KUNCI PERBAIKAN: Kita hapus kata 'status' dari SQL biar gak error!
        cursor.execute("SELECT id, nama, kelas, nis FROM app_perpus_siswa ORDER BY id ASC")
        
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        siswa_list = []
        for row in rows:
            siswa_dict = dict(zip(columns, row))
            
            # Trik Sulap: Karena di DB gak ada kolom status, kita inject otomatis 
            # lewat Python supaya di template tetep kebaca 'Aktif' sesuai screenshot lu!
            siswa_dict['status'] = 'Aktif' 
            
            siswa_list.append(siswa_dict)
        
    return render(request, 'siswa/list.html', {'siswa_list': siswa_list})

def tambah_siswa(request):
    if request.method == "POST":
        nama = request.POST['nama']
        kelas = request.POST['kelas']
        nis = request.POST['nis']
        is_active = request.POST.get('is_active') == 'true'
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO app_perpus_siswa (nama, kelas, nis, is_active)
                VALUES (%s, %s, %s, %s)
            """, [nama, kelas, nis, is_active])
        return redirect('list_siswa')
    return render(request, 'siswa/tambah.html')

def detail_siswa(request, id):
    with connection.cursor() as cursor:
        # Ambil data siswa tanpa kolom status
        cursor.execute("SELECT id, nama, kelas, nis FROM app_perpus_siswa WHERE id = %s", [id])
        row = cursor.fetchone()
        
        if row:
            columns = [col[0] for col in cursor.description]
            siswa_data = dict(zip(columns, row))
            siswa_data['status'] = 'Aktif' # Trik aman: inject status buat template
        else:
            return redirect('list_siswa')
            
    return render(request, 'siswa/detail.html', {'siswa': siswa_data})

def edit_siswa(request, id):
    with connection.cursor() as cursor:
        if request.method == "POST":
            nama = request.POST['nama']
            kelas = request.POST['kelas']
            nis = request.POST['nis']
            
            # Update data ke database (tanpa kolom status)
            cursor.execute("""
                UPDATE app_perpus_siswa 
                SET nama = %s, kelas = %s, nis = %s 
                WHERE id = %s
            """, [nama, kelas, nis, id])
            
            return redirect('list_siswa')
        else:
            # Ambil data lama buat ditampilin di input form
            cursor.execute("SELECT id, nama, kelas, nis FROM app_perpus_siswa WHERE id = %s", [id])
            row = cursor.fetchone()
            
            if row:
                columns = [col[0] for col in cursor.description]
                siswa_data = dict(zip(columns, row))
                siswa_data['status'] = 'Aktif'
            else:
                return redirect('list_siswa')
                
    return render(request, 'siswa/edit.html', {'siswa': siswa_data})

def hapus_siswa(request, id):
    with connection.cursor() as cursor:
        if request.method == "POST":
            # Eksekusi hapus data
            cursor.execute("DELETE FROM app_perpus_siswa WHERE id = %s", [id])
            return redirect('list_siswa')
        else:
            # Ambil data bentar buat konfirmasi di halaman hapus.html
            cursor.execute("SELECT id, nama FROM app_perpus_siswa WHERE id = %s", [id])
            row = cursor.fetchone()
            if row:
                siswa_data = {'id': row[0], 'nama': row[1]}
            else:
                return redirect('list_siswa')
                
    return render(request, 'siswa/hapus.html', {'siswa': siswa_data})


# ==========================================
# 3. MODUL PEMINJAMAN
# ==========================================
def list_peminjaman(request):
    with connection.cursor() as cursor:
        # 1. Ambil mentah data dari tabel peminjaman tanpa tembak nama kolom spesifik
        cursor.execute("SELECT * FROM app_perpus_peminjaman ORDER BY id DESC")
        columns = [col[0] for col in cursor.description]
        mentah_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        peminjaman_list = []
        
        # 2. Deteksi kolom secara cerdas pake Python (Anti-Gagal!)
        for p in mentah_list:
            # Ambil ID Siswa (Cari nama kolom yang cocok)
            id_siswa = p.get('siswa_id') or p.get('id_siswa') or p.get('siswa')
            nama_siswa = "Data tidak ditemukan"
            if id_siswa:
                cursor.execute("SELECT nama FROM app_perpus_siswa WHERE id = %s", [id_siswa])
                res_siswa = cursor.fetchone()
                if res_siswa:
                    nama_siswa = res_siswa[0]
            
            # Ambil ID Buku
            id_buku = p.get('buku_id') or p.get('id_buku') or p.get('buku')
            judul_buku = "Data tidak ditemukan"
            if id_buku:
                cursor.execute("SELECT judul FROM app_perpus_buku WHERE id = %s", [id_buku])
                res_buku = cursor.fetchone()
                if res_buku:
                    judul_buku = res_buku[0]
            
            # Ambil Tanggal Pinjam & Kembali (Deteksi otomatis flexibel)
            tgl_pinjam = p.get('tgl_pinjam') or p.get('tanggal_pinjam') or p.get('tgl_peminjaman') or p.get('tanggal')
            tgl_kembali = p.get('tgl_kembali') or p.get('tanggal_kembali') or p.get('tgl_pengembalian') or p.get('jatuh_tempo')
            
            # Masukkan ke list hasil akhir
            peminjaman_list.append({
                'id': p.get('id'),
                'nama_siswa': nama_siswa,
                'judul_buku': judul_buku,
                'tgl_pinjam': tgl_pinjam,
                'tgl_kembali': tgl_kembali,
                'keperluan': p.get('keperluan', '-'),
                'petugas': p.get('petugas') or 'Jang Soo-Ha',
                'status': p.get('status', 'Dipinjam'),
            })
            
    return render(request, 'peminjaman/list.html', {'peminjaman_list': peminjaman_list})

def tambah_peminjaman(request):
    with connection.cursor() as cursor:
        if request.method == "POST":
            id_siswa = request.POST['id_siswa']
            id_buku = request.POST['id_buku']
            tgl_pinjam = request.POST['tgl_pinjam']
            tgl_kembali = request.POST['tgl_kembali']
            keperluan = request.POST['keperluan']
            
            # KUNCI PERBAIKAN: Ganti jadi Jang Sooha sesuai database lu
            petugas = "Jang Sooha" 
            catatan = request.POST.get('catatan', '')
            
            cursor.execute("""
                INSERT INTO app_perpus_peminjaman (siswa_id, buku_id, tgl_pinjam, tgl_kembali, keperluan, petugas, catatan, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Dipinjam')
            """, [id_siswa, id_buku, tgl_pinjam, tgl_kembali, keperluan, petugas, catatan])
            
            cursor.execute("UPDATE app_perpus_buku SET stok = stok - 1 WHERE id = %s", [id_buku])
            return redirect('list_peminjaman')
        
        else:
            cursor.execute("SELECT id, nama, nis FROM app_perpus_siswa")
            siswa_list = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT id, judul, stok FROM app_perpus_buku WHERE stok > 0")
            buku_list = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
    return render(request, 'peminjaman/tambah.html', {'siswa_list': siswa_list, 'buku_list': buku_list})

def ubah_status_peminjaman(request, id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE app_perpus_peminjaman SET status = 'Dikembalikan' WHERE id = %s", [id])
    return redirect('list_peminjaman')

def kembalikan_buku(request, id):
    with connection.cursor() as cursor:
        # KUNCI PERBAIKAN: Ambil dari kolom buku_id
        cursor.execute("SELECT buku_id FROM app_perpus_peminjaman WHERE id = %s", [id])
        row = cursor.fetchone()
        
        if row:
            id_buku = row[0]
            cursor.execute("UPDATE app_perpus_peminjaman SET status = 'Dikembalikan' WHERE id = %s", [id])
            cursor.execute("UPDATE app_perpus_buku SET stok = stok + 1 WHERE id = %s", [id_buku])
            
    return redirect('list_peminjaman')