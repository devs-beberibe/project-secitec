
from multiprocessing import context
from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.

from .models import Secretary

def index(request):
    return render(request, 'called/index.html')

def create(request):
    list_secretary = Secretary.objects.all()
    context = { 'list_secretary' : list_secretary}
    return render(request, 'called/create.html', context)

def query(request):
    return render(request, 'called/query.html')
