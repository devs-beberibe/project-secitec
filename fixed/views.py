from django.shortcuts import render

from .forms import FichaVerificacaoComponentesForm
from .models import Componente

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
