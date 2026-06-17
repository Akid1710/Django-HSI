from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # URL Buku
    path('buku/', views.list_buku, name='list_buku'),
    path('buku/tambah/', views.tambah_buku, name='tambah_buku'),
    path('buku/detail/<int:id>/', views.detail_buku, name='detail_buku'),
    path('buku/edit/<int:id>/', views.edit_buku, name='edit_buku'),
    path('buku/hapus/<int:id>/', views.hapus_buku, name='hapus_buku'),
    
    # URL Siswa
    path('siswa/', views.list_siswa, name='list_siswa'),
    path('siswa/tambah/', views.tambah_siswa, name='tambah_siswa'),
    path('siswa/detail/<int:id>/', views.detail_siswa, name='detail_siswa'),
    path('siswa/edit/<int:id>/', views.edit_siswa, name='edit_siswa'),
    path('siswa/hapus/<int:id>/', views.hapus_siswa, name='hapus_siswa'),
    
    # URL Peminjaman
    path('peminjaman/', views.list_peminjaman, name='list_peminjaman'),
    path('peminjaman/tambah/', views.tambah_peminjaman, name='tambah_peminjaman'),
    path('peminjaman/status/<int:id>/', views.ubah_status_peminjaman, name='ubah_status_peminjaman'),
    path('peminjaman/kembalikan/<int:id>/', views.kembalikan_buku, name='kembalikan_buku'),
]