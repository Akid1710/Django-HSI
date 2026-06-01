from django.shortcuts import render

def home(request):
    return render(request, 'profile_home.html')

def biodata(request):
    return render(request, 'biodata.html')

def jadwal(request):
    return render(request, 'jadwal.html')

def galeri(request):
    return render(request, 'galeri.html')

def feedback(request):
    return render(request, 'feedback.html')