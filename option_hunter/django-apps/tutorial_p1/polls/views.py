from django.shortcuts import render
from django.http import HttpResponse

# create a simple view
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

