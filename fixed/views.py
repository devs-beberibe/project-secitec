from django.shortcuts import render

from .forms import FichaVerificacaoComponentesForm
from .models import Componente, FichaVerificacaoComponentes

def create(request):

    componentes = Componente.objects.all()

    if request.method == "POST":
        ficha_form = FichaVerificacaoComponentesForm(request.POST)

        if ficha_form.is_valid():
            ficha = ficha_form.save()

    context = {
        "ficha_form" : FichaVerificacaoComponentesForm(),
        "componentes" : componentes,
    }

    return render(request, "fixed/create.html", context=context)


def list_fix(request):
    fixed = FichaVerificacaoComponentes.objects.all()

    context = {
        "fixed": fixed
    }

    return render(request, "fixed/list_fix.html", context=context)