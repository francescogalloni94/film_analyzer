from . import film_utility
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy
import json
from . import confusion_matrix as matrix
from bson import json_util
from sklearn.metrics import confusion_matrix

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client['IRDB']
film_collection = db['films']
film_list = list()
true_labels = list()

def getRelatedByPlot(film_id):
    filmDetails = film_utility.getFilmDetails(film_id)
    recommended = filmDetails['recommendations']['results']
    global film_list
    film_list = list()
    film_overviews = list()
    recommended_titles = list()
    global true_labels
    true_labels = list()
    recommended_titles.append(filmDetails['title'])
    film_list.append(filmDetails)
    film_overviews.append(filmDetails['overview'])

    for film in recommended:
         details = film_utility.getFilmDetails(str(film['id']))
         film_list.append(details)
         film_overviews.append(details['overview'])
         recommended_titles.append((details['title']))
         true_labels.append("relevant")

    DBfilmDetails = film_collection.find({"title":{"$nin":recommended_titles}},{"_id": 0 })

    for film in DBfilmDetails:
        #film_list.append(json.dumps(film,default=json_util.default))
        film_list.append(dict(film))
        film_overviews.append(film['overview'])
        true_labels.append("non relevant")

    details_to_return = cosineSimilarity(film_overviews)
    predicted_labels = getPredictedLabels(details_to_return)


    precision = computeConfusionMatrix(true_labels,predicted_labels,"./public/images/plot.png")
    companies = getRelatedByProductionCompanies()
    cast = getRelatedByCast()
    crew = getRelatedByCrew()
    to_return = dict()
    to_return['detailsPlot'] = details_to_return
    to_return['precisionPlot'] = precision
    to_return['detailsCompany'] = companies['details']
    to_return['precisionCompany'] = companies['precision']
    to_return['detailsCast'] = cast['details']
    to_return['precisionCast'] = cast['precision']
    to_return['detailsCrew'] = crew['details']
    to_return['precisionCrew'] = crew['precision']
    return to_return



def cosineSimilarity(toAnalyze,tokenizer=True):
    global film_list
    if tokenizer:
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(toAnalyze)
    else:
        tfidf_vectorizer = TfidfVectorizer(tokenizer=lambda x: x,stop_words=None, lowercase=False)
        tfidf_matrix = tfidf_vectorizer.fit_transform(toAnalyze)
    similarity_array = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
    ordered_array = numpy.argsort(similarity_array[0])[::-1][:21]
    ordered_array = numpy.delete(ordered_array, 0)

    details_to_return = list()
    for element in ordered_array:
        details_to_return.append(film_list[element])

    return details_to_return


def computeConfusionMatrix(true_labels,predicted_labels,filename):
    cm = confusion_matrix(true_labels, predicted_labels, labels=["relevant", "non relevant"])
    matrix.plot_confusion_matrix(cm, target_names=["relevant", "non relevant"],filename=filename)
    tp = cm[0][0]
    fn = cm[0][1]
    fp = cm[1][0]
    tn = cm[1][1]
    precision = tp / float(tp + fp)
    return precision


def getPredictedLabels(details_to_return):
    global film_list
    predicted_labels = list()
    count = 0
    for element in film_list:
        if count != 0:
            control = False
            for details in details_to_return:
                if element == details:
                    control = True
                    break
            if control:
                predicted_labels.append("relevant")
            else:
                predicted_labels.append("non relevant")

        count = count + 1
    return predicted_labels



def getRelatedByGenre():
    global film_list
    genres_list = list()
    for element in film_list:
        genres = list()
        for genre in element['genres']:
            genres.append(genre['name'])
        genres_list.append(genres)



def getRelatedByCast():
    global film_list
    global true_labels
    cast_list = list()
    for element in film_list:
        cast = list()
        for member in element['credits']['cast']:
            cast.append(member['name'])
        cast_list.append(cast)
    details_to_return = cosineSimilarity(cast_list,tokenizer=False)
    predicted_labels = getPredictedLabels(details_to_return)
    precision = computeConfusionMatrix(true_labels,predicted_labels, "./public/images/cast.png")
    to_return = dict()
    to_return['details'] = details_to_return
    to_return['precision'] = precision
    return to_return




def getRelatedByCrew():
    global film_list
    global true_labels
    crew_list = list()
    for element in film_list:
        crew = list()
        for member in element['credits']['crew']:
            crew.append(member['name'])
        crew_list.append(crew)
    details_to_return = cosineSimilarity(crew_list,tokenizer=False)
    predicted_labels = getPredictedLabels(details_to_return)
    precision = computeConfusionMatrix(true_labels,predicted_labels,"./public/images/crew.png")
    to_return = dict()
    to_return['details'] = details_to_return
    to_return['precision'] = precision
    return to_return



def getRelatedByProductionCompanies():
    global film_list
    global true_labels
    company_list = list()
    for element in film_list:
        companies = list()
        for company in element['production_companies']:
            companies.append(company['name'])
        company_list.append(companies)

    details_to_return = cosineSimilarity(company_list,tokenizer=False)
    predicted_labels = getPredictedLabels(details_to_return)
    precision = computeConfusionMatrix(true_labels, predicted_labels, "./public/images/production_companies.png")
    to_return = dict()
    to_return['details'] = details_to_return
    to_return['precision'] = precision
    return to_return






