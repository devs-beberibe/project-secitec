
from ast import Return
import re
from subprocess import call
from telnetlib import STATUS
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

def detail(request):
    call_id = request.GET['call_id']
    call = Call.objects.filter(pk=call_id).get
    return render(request, 'called/detail.html', {'call' : call})

def create(request):
    if request.method == 'POST':
        call = Call()
        call.secretary_sector=Secretary.objects.get(pk=request.POST['secretary']).id
        call.requester=request.POST['requester'] 
        call.problem=request.POST['problem'] 

        call.save()
        
        #return HttpResponse("Postagem bem sucedida seu chamado é o {}".format(call.id))
        return render(request, "called/success.html", {'id' : call.id})
    return HttpResponse("Método não permitido", status=403)

def list(request, status='OPN'):
    calleds = Call.objects.filter(status=status)
    return render(request, 'called/list.html', {'list_called' : calleds})

def edit_status(request, id):
    called = get_object_or_404(Call, pk=id)
    called.status = request.POST["status"]
    called.save()
    return list(request)


def query(request):
    return render(request, 'called/query.html') 
    

