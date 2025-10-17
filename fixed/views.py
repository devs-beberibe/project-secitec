from django.shortcuts import render, get_object_or_404

from django.contrib import messages

from .forms import FichaDeManutencaoForm
from .models import Componente, FichaDeManutencao

def create(request):

    componentes = Componente.objects.all()

    if request.method == "POST":
        ficha_form = FichaDeManutencaoForm(request.POST)

        if ficha_form.is_valid():
            ficha = ficha_form.save()

            messages.success(request, f'Ficha de Manutenção, entrada, criada com sucesso! Número "{ficha.id}"')
        else:
            messages.error(request, f'Erro ao tentar criar a Ficha de Manutenção - Entrada')
            print(ficha_form.errors)
            context = {
                "ficha_form" : FichaDeManutencaoForm(),
                "componentes" : componentes,
            }
            
    context = {
        "ficha_form" : FichaDeManutencaoForm(),
        "componentes" : componentes,
    }

    return render(request, "fixed/create.html", context=context)


def update(request, id):

    ficha = get_object_or_404(FichaDeManutencao, pk=id)
    componentes = Componente.objects.all()

    if request.method == "POST":
        ficha_form = FichaDeManutencaoForm(request.POST, instance=ficha)

        if ficha_form.is_valid():
            ficha = ficha_form.save()

            messages.success(request, f'Ficha de Manutenção, entrada, criada com sucesso! Número "{ficha.id}"')
            
        else:
            messages.error(request, f'Erro ao tentar criar a Ficha de Manutenção - Entrada')

            context = {
                "ficha_form" : FichaDeManutencaoForm(),
                "componentes" : componentes,
            }
            
    context = {
        "ficha_form" : FichaDeManutencaoForm(instance=ficha),
        "componentes" : componentes,
    }

    return render(request, "fixed/create.html", context=context)


def list_fix(request):
    fixed = FichaDeManutencao.objects.all()
    
    context = {
        "fixed": fixed
    }

    return render(request, "fixed/list_fix.html", context=context)