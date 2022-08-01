from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse('Главная страница Yatube')

def group_posts(request, pk):
    return HttpResponse(f'Пост номер {pk}')
