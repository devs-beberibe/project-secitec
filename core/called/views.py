
from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.

def index(request):
    return render(request, 'called/index.html')

def create(request):
    return HttpResponse('Create call')

def query(request):
    return HttpResponse("Page query")
