from django.urls import path
from . import views

urlpatterns = [
    path("", views.santri_home, name="santri_home"),
    path("biodata/", views.biodata, name="biodata"),
    path("jadwal/", views.jadwal, name="jadwal"),
    path("galeri/", views.galeri, name="galeri"),
    path("feedback/", views.feedback, name="feedback"),
]