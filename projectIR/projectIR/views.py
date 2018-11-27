from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from . import film_utility
from. import film_analyzer

def homepage(request):
    return render(request,'homepage.html')

def film(request):
    return render(request, 'film.html')

def searchFilm(request):
    TMDBRes = film_utility.searchFilmOnTMDB(request.GET.get('film',''))
    return JsonResponse(TMDBRes)

def getFilmDetails(request):
    filmDetails = film_utility.getFilmDetails(request.GET.get('id',''))
    return JsonResponse(filmDetails)

def getRelatedByPlot(request):
    film_id = request.GET.get('currentFilm','')
    relatedByPlot = film_analyzer.getRelatedByPlot(film_id)
    return JsonResponse(relatedByPlot,safe=False)
