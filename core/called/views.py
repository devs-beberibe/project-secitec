
import re
from sre_constants import CALL
from subprocess import call
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
# Create your views here.

from .models import Secretary, Call

def index(request):
    return render(request, 'called/index.html')

def create_page(request):
    list_secretary = Secretary.objects.all()
    context = { 'list_secretary' : list_secretary}
    return render(request, 'called/create.html', context)

def create(request):
    print('create======================')
    if request.method == 'POST':
        call = Call()
        call.secretary_sector=request.POST['secretary']
        call.requester=request.POST['requester'] 
        call.problem=request.POST['problem'] 

        call.save()
        
        return HttpResponse("Postagem bem sucedida")
    return HttpResponse("Método não permitido", status=403)
    ''

def query(request, call_id):
    call = get_object_or_404(Call, pk=call_id)
    return render(request, 'called/query.html', {'call' : call})
