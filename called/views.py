from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404

from django.core.paginator import Paginator

from .models import Secretary, Call, Tecnico

def index(request):
    return render(request, 'called/index.html')

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
        
        #return HttpResponse("Postagem bem sucedida seu chamado é o {}".format(call.id))
        return render(request, "called/information.html",
                {
                    'title_info': f"Postagem bem sucedida seu chamado é o {call.id}",
                    'redirect' : '/',
                    'text_redirect' : "Voltar para Home"
                }
            )

    else :
        list_secretary = Secretary.objects.all()
        context = { 'list_secretary' : list_secretary}
        return render(request, 'called/create.html', context)


    return HttpResponse("Método não permitido", status=403)

@login_required
def close(request, id_call):
    call = get_object_or_404(Call, pk=id_call)
    tecnicos  = Tecnico.objects.all()    
    
    if request.method == 'POST':    
        for aux in tecnicos:
            if request.POST.get(aux.user.username, False):
                tecnico = Tecnico.objects.filter(
                    user_id = request.POST.get(aux.user.username, False)
                )[0]
                tecnico.called.add(call.id)
                tecnico.save()
        
        if request.POST.get('date_end', False):
            data_end = request.POST['date_end']
        else:    
            data_end = timezone.now()
        
        if request.POST.get('solution', False):
            call.solution = request.POST.get('solution', False)
        call.date_end = data_end
        call.save(force_update=True)
                   
        return edit_status(request, id_call, 'encerrados')
    
    else:
        context = {
            'call' : call,
            'tecnicos': tecnicos,
        }
        
        return render(request, 'called/close.html', {
            'call' : call,
            'tecnicos': tecnicos,
        })
    
    
@login_required
def list(request):

    stts = request.GET.get('status')
    page = request.GET.get('page')

    for row in Call.STATUS_CALLED:
        if row[1] == stts:
            stts = row[0]
    
    called_all = Call.objects.filter(status=stts)
    paginator = Paginator(called_all, 8)
    
    called = paginator.get_page(page)
    
    return render(request, 'called/list.html', 
            {
                'called' : called,
                'page': page,
                'status': stts,
            }
        )

@login_required
def edit_status(request, id, status):
    called = get_object_or_404(Call, pk=id)
    
    # Caso o chamado seja encerrado ele não pode mais voltar 
    # para a listagem
    if (called.status == Call.STATUS_CALLED[2][0]):
        return render(request,'called/information.html',
            {'title_info': 'Esse chamado já está encerado'})
        
    for row in Call.STATUS_CALLED:
        if row[1] == status:
            status = row[0]
            
    called.status = status
    called.save()

    return list(request, status, 1)


def query(request):
    return render(request, 'called/query.html') 
    

