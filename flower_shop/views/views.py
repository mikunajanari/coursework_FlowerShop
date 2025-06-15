from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return HttpResponse("Головна сторінка працює!")

def home(request):
    return render(request, 'flower_shop/index.html')