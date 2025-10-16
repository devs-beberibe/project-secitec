from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Secretary, Call, Tecnico
from .forms import CallForm

def index(request):
    return render(request, 'core/index.html')

def detail(request, id_call):
    call = Call.objects.get(pk=id_call)
    tecnicos = Tecnico.objects.filter(called=id_call)

    return render(request, 'called/detail.html', {'call' : call, 'tecnicos': tecnicos})

def create(request):
    if request.method == 'POST':
        form_call = CallForm(request.POST)

        if form_call.is_valid():
            call = form_call.save()

            messages.info(request, f'{call.id}')
        
        else:
            form_call = CallForm()
            context = { 'form_call' : form_call}
            return render(request, 'called/create.html', context)

    form_call = CallForm()
    context = { 'form_call' : form_call}
    return render(request, 'called/create.html', context)


@login_required
def close(request, id_call):
    call = get_object_or_404(Call, pk=id_call)
    tecnicos  = Tecnico.objects.all()    
    
    if request.method == 'POST':    
        for tecnico in tecnicos:
            if request.POST.get(tecnico.user.username, False):
                tecnico = Tecnico.objects.filter(
                    user_id = request.POST.get(tecnico.user.username, False)
                )[0]
                tecnico.called.add(call.id)
                tecnico.save()
        print(">>>>>>>", timezone.now())
        print(">>>>>>>", request.POST.get('solution', ''))
        print(">>>>>>>", request.POST.get('date_end', '2024-03-20'))
        call.solution = request.POST.get('solution', '')
        call.date_end = request.POST.get('date_end', '2024-03-20')
        call.status = 'CLS'
        call.save()
                   
        return redirect('detail', id_call)

    context = {
        'call' : call,
        'tecnicos': tecnicos,
    }
    
    return render(request, 'called/close.html', context=context)
    
    
@login_required
def list(request):
    status = request.GET.get('status')
    page = request.GET.get('pagina')

    for row in Call.STATUS_CALLED:
        if row[1] == status:
            status = row[0]
    
    called_all = Call.objects.filter(status=status)
    paginator = Paginator(called_all, 8)
    
    called = paginator.get_page(page)

    context = {
        'called' : called,
        'status': status,
    }

    return render(request, 'called/list.html', context=context)


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
    
    return index(request)


def query(request):
    return render(request, 'called/query.html') 
    

