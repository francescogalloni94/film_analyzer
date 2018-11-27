import requests
import time

Tmdb_APIKEY = '32001eea54ed498b049c61a935afdb6e'


def searchSimilarFilmOnTMDB(imdb_id):
    r = requests.get('https://api.themoviedb.org/3/movie/'+imdb_id+'/similar?api_key='+Tmdb_APIKEY+'&language=en-US&external_source=imdb_id')
    return r.json()

def searchFilmOnTMDB(title):
    r = requests.get('https://api.themoviedb.org/3/search/movie?api_key='+Tmdb_APIKEY+'&query='+title+'&language=en-US&page=1&include_adult=false')
    return r.json()

def getFilmDetails(imdb_id):
    control = True
    while control:
        r = requests.get('https://api.themoviedb.org/3/movie/'+imdb_id+'?api_key='+Tmdb_APIKEY+'&language=en-US&append_to_response=recommendations,credits')
        if r.status_code==200:
            control = False
        else:
            time.sleep(10)
    return r.json()


def getReccomendedFilm(imdb_id):
    r = requests.get('https://api.themoviedb.org/3/movie/'+imdb_id+'/recommendations?api_key='+Tmdb_APIKEY+'&language=en-US&page=1')
    return r.json()

