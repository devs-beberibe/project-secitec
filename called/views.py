from sqlite3 import Row
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

def detail(request):
    call_id = request.GET['call_id']
    call = Call.objects.filter(pk=call_id).get
    return render(request, 'called/detail.html', {'call' : call})

def create(request):
    if request.method == 'POST':
        call = Call()
        call.secretary_sector=Secretary.objects.get(pk=request.POST['secretary'])
        call.requester=request.POST['requester'] 
        call.problem=request.POST['problem'] 

        call.save()
        
        return render(request, "called/success.html", {'id' : call.id})
    return HttpResponse("Método não permitido", status=403)

def list(request, stts, page):
    
    for row in Call.STATUS_CALLED:
        if row[1] == stts:
            stts = row[0]
    
    called = Call.objects.filter(status=stts)[(page-1)*8:page*8]
    return render(request, 'called/list.html', {'list_called' : called})

def edit_status(request, id):
    called = get_object_or_404(Call, pk=id)
    called.status = request.POST["status"]
    called.save()
    return list(request, 'OPN')


def query(request):
    return render(request, 'called/query.html') 
    

