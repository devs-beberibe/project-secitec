
from django.http import HttpResponse
# Create your views here.

def index(request):
    return HttpResponse('Page called index')

def create(request):
    return HttpResponse('Create call')
