import requests
import time
from pymongo import MongoClient

client = MongoClient()

client = MongoClient('localhost', 27017)

db = client['IRDB']

mongo_collection = db['films']
genres_collection = db['genres']

Tmdb_APIKEY = '32001eea54ed498b049c61a935afdb6e'

r = requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key="+Tmdb_APIKEY+"&language=en-US")
r_json = r.json()
genres = r_json['genres']
genres_collection.insert_many(genres)

film_collection = dict()

for genre in r_json['genres']:
	genreId = str(genre['id'])
	control = True
	while control:
		films = requests.get("https://api.themoviedb.org/3/discover/movie?api_key="+Tmdb_APIKEY+"&language=en-US&with_genres="+genreId+"&page=1")
		if films.status_code == 200:
			control = False
			film_collection[genreId] = (films.json())['results']
		else:
			time.sleep(10)

	control = True
	while control:
		films = requests.get("https://api.themoviedb.org/3/discover/movie?api_key="+Tmdb_APIKEY+"&language=en-US&with_genres="+genreId+"&page=2")
		if films.status_code == 200:
			control = False
			film_collection[genreId] = film_collection[genreId] + (films.json())['results']
		else:
			time.sleep(10)
	control = True
	while control:
		films = requests.get("https://api.themoviedb.org/3/discover/movie?api_key="+Tmdb_APIKEY+"&language=en-US&with_genres="+genreId+"&page=3")
		if films.status_code == 200:
			control = False
			film_collection[genreId] = film_collection[genreId] + (films.json())['results']
		else:
			time.sleep(10)
	control = True
	while control:
		films = requests.get("https://api.themoviedb.org/3/discover/movie?api_key="+Tmdb_APIKEY+"&language=en-US&with_genres="+genreId+"&page=4")
		if films.status_code == 200:
			control = False
			film_collection[genreId] = film_collection[genreId] + (films.json())['results']
		else:
			time.sleep(10)
	control = True
	while control:
		films = requests.get("https://api.themoviedb.org/3/discover/movie?api_key="+Tmdb_APIKEY+"&language=en-US&with_genres="+genreId+"&page=5")
		if films.status_code == 200:
			control = False
			film_collection[genreId] = film_collection[genreId] + (films.json())['results']
		else:
			time.sleep(10)
	control = True
	while control:
		films = requests.get("https://api.themoviedb.org/3/discover/movie?api_key="+Tmdb_APIKEY+"&language=en-US&with_genres="+genreId+"&page=6")
		if films.status_code == 200:
			control = False
			film_collection[genreId] = film_collection[genreId] + (films.json())['results']
		else:
			time.sleep(10)

film_to_insert = list()
for collection in film_collection:
	for film in film_collection[collection]:
		id_to_search = str(film['id'])
		control = True
		while control:
			search = requests.get('https://api.themoviedb.org/3/movie/'+id_to_search+'?api_key='+Tmdb_APIKEY+'&language=en-US&append_to_response=credits')
			if search.status_code == 200:
				control = False
				title = (search.json())['title']
				if mongo_collection.find({"title":title}).count() == 0:
					#film_to_insert.append(search.json())
					mongo_collection.insert_one(search.json())
			else:
				time.sleep(10)

#mongo_collection.insert_many(film_to_insert)


