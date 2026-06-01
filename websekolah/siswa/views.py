from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
from django.utils.html import escape

# ==========================================
# 1. FUNGSI BANTUAN DATABASE (HARUS DI ATAS)
# ==========================================

def dictfetchall(cursor):
    """Mengubah semua hasil query menjadi list of dictionary."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dictfetchone(cursor):
    """Mengubah satu hasil query menjadi dictionary."""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(zip(columns, row))


# ==========================================
# 2. FUNGSI TAMPILAN (VIEWS)
# ==========================================

def siswa_list(request):
    """Halaman Utama dengan Fitur Pencarian & Urut Abjad"""
    # 1. Tangkap kata kunci dari form pencarian (jika ada)
    keyword = request.GET.get('q', '').strip()
    
    with connection.cursor() as cursor:
        if keyword:
            # Jika user sedang mencari sesuatu (Gunakan ILIKE agar case-insensitive / bebas huruf besar-kecil)
            cursor.execute(
                """
                SELECT * FROM siswa 
                WHERE nama ILIKE %s
                ORDER BY nama ASC
                """,
                [f"%{keyword}%"]
            )
        else:
            # Jika tidak ada pencarian, tampilkan semua seperti biasa
            cursor.execute(
                """
                SELECT * FROM siswa 
                ORDER BY nama ASC
                """
            )
        data_siswa = dictfetchall(cursor)
    
    # 2. Lempar data_siswa dan keyword-nya ke template
    return render(request, 'list.html', {
        'data': data_siswa,
        'keyword': keyword  # Dikirim balik biar teks di kotak pencarian gak ilang setelah diklik
    })


def siswa_detail(request, id):
    """Halaman Detail: Melihat Profil 1 Siswa Berdasarkan ID"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM siswa
            WHERE id = %s
            """,
            [id]
        )
        siswa = dictfetchone(cursor) # Sekarang fungsinya pasti kebaca dengan benar

    return render(request, 'detail.html', {
        'siswa': siswa,
    })


def siswa_create(request):
    """Halaman Tambah: Memasukkan Data Siswa Baru"""
    if request.method == 'POST':
        # Tarik semua data dari form input
        nama = request.POST.get('nama', '').strip()
        umur = request.POST.get('umur', '').strip()
        tgl_lahir = request.POST.get('tgl_lahir', '').strip()
        status_hadir = request.POST.get('status_hadir', '').strip()
        nilai_akhir = request.POST.get('nilai_akhir', '').strip()

        # Eksekusi INSERT lengkap ke semua kolom database
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO siswa (nama, umur, tgl_lahir, status_hadir, nilai_akhir)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [nama, umur, tgl_lahir, status_hadir, nilai_akhir]
            )
        return redirect('siswa_list')

    return render(request, 'form.html')


def siswa_update(request, id):
    # 1. Ambil data siswa lama dari database berdasarkan ID
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM siswa WHERE id = %s", [id])
        siswa = dictfetchone(cursor)
    
    if not siswa:
        return redirect('siswa_list')

    # 2. Proses saat user klik tombol "Simpan Perubahan" (POST)
    if request.method == 'POST':
        nama_baru = request.POST.get('nama', '').strip()
        umur_baru = request.POST.get('umur', '').strip()
        tgl_lahir_baru = request.POST.get('tgl_lahir', '').strip()
        status_hadir_baru = request.POST.get('status_hadir', '').strip()
        nilai_akhir_baru = request.POST.get('nilai_akhir', '').strip()

        # Eksekusi query UPDATE SQL untuk semua kolom
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE siswa 
                SET nama = %s, 
                    umur = %s, 
                    tgl_lahir = %s, 
                    status_hadir = %s, 
                    nilai_akhir = %s 
                WHERE id = %s
                """,
                [nama_baru, umur_baru, tgl_lahir_baru, status_hadir_baru, nilai_akhir_baru, id]
            )
        return redirect('siswa_list')

    # Kirim data 'siswa' ke template form
    return render(request, 'form.html', {'siswa': siswa})


def siswa_delete(request, id):
    """Halaman Konfirmasi & Fungsi Hapus Siswa"""
    # 1. Ambil data siswa dulu buat ditampilin namanya di halaman konfirmasi
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM siswa WHERE id = %s", [id])
        siswa = dictfetchone(cursor)
    
    # Kalau siswa gak ketemu, balikin ke halaman utama
    if not siswa:
        return redirect('siswa_list')

    # 2. Proses kalau user klik tombol "Ya, Hapus" (POST)
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM siswa WHERE id = %s
                """,
                [id]
            )
        return redirect('siswa_list')

    # 3. Kalau cuma diakses biasa (GET), tampilin halaman konfirmasi baru
    return render(request, 'delete_confirm.html', {'siswa': siswa})