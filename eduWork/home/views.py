from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def index (request):
    return render(request, 'index.html')

def studentprofile (request):
    return HttpResponse("student profile page")

def announcement (request):
    return HttpResponse("announcement page")

def contract (request):
    return HttpResponse("contract page")

def job_history (request):
    return HttpResponse("job history page")

