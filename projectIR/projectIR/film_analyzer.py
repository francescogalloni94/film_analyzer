from . import film_utility
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy
from . import confusion_matrix as matrix
from sklearn.metrics import confusion_matrix

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client['IRDB']
film_collection = db['films']
genres_collection = db['genres']
precisions_collection = db['precisions']
film_list = list()
true_labels = list()
reccomended_films = list()
titles = list()


def getRelatedByPlot(film_id):
    filmDetails = film_utility.getFilmDetails(film_id)
    recommended = filmDetails['recommendations']['results']
    global film_list
    global reccomended_films
    film_list = list()
    film_overviews = list()
    recommended_titles = list()
    global true_labels
    true_labels = list()
    recommended_titles.append(filmDetails['title'])
    film_list.append(filmDetails)
    plot_similarity_reccomended = list()
    plot_similarity_reccomended.append(filmDetails['overview'])
    film_overviews.append(filmDetails['overview'])

    for film in recommended:
         details = film_utility.getFilmDetails(str(film['id']))
         film_list.append(details)
         reccomended_films.append(details)
         film_overviews.append(details['overview'])
         plot_similarity_reccomended.append(details['overview'])
         recommended_titles.append((details['title']))
         true_labels.append("relevant")

    DBfilmDetails = film_collection.find({"title":{"$nin":recommended_titles}},{"_id": 0 })

    for film in DBfilmDetails:
        film_list.append(dict(film))
        film_overviews.append(film['overview'])
        true_labels.append("non relevant")

    details_to_return = cosineSimilarity(film_overviews)
    predicted_labels = getPredictedLabels(details_to_return)


    precision = computeConfusionMatrix(true_labels,predicted_labels,"./public/images/plot.png")
    companies = getRelatedByProductionCompanies()
    cast = getRelatedByCast()
    crew = getRelatedByCrew()
    genres = getRelatedByGenre()
    genres_cosine = getRelatedByGenresCosineSimilarity()
    plot_similarity_array = cosineSimilarityReccomended(plot_similarity_reccomended)
    recommended_titles.pop(0)
    global titles
    titles = recommended_titles
    to_return = dict()
    precision_db = dict()

    precision_db['id'] = film_list[0]['id']
    to_return['recommendedTitles'] = titles
    to_return['detailsPlot'] = details_to_return
    to_return['precisionPlot'] = precision
    to_return['similarityPlot'] = plot_similarity_array.tolist()
    precision_db['precisionPlot'] = precision
    to_return['detailsCompany'] = companies['details']
    to_return['precisionCompany'] = companies['precision']
    to_return['similarityCompany'] = companies['companiesSimilarity']
    precision_db['precisionCompany'] = companies['precision']
    to_return['detailsCast'] = cast['details']
    to_return['precisionCast'] = cast['precision']
    to_return['similarityCast'] = cast['castSimilarity']
    precision_db['precisionCast'] = cast['precision']
    to_return['detailsCrew'] = crew['details']
    to_return['precisionCrew'] = crew['precision']
    to_return['similarityCrew'] = crew['crewSimilarity']
    precision_db['precisionCrew'] = crew['precision']
    if 'details' in genres:
        to_return['detailsGenres'] = genres['details']
        to_return['precisionGenres'] = genres['precision']
        precision_db['precisionGenres'] = genres['precision']

    to_return['similarityGenres'] = genres['genresSimilarity']
    to_return['detailsGenresCosine'] = genres_cosine['details']
    to_return['precisionGenresCosine'] = genres_cosine['precision']
    precision_db['precisionGenresCosine'] = genres_cosine['precision']
    if precisions_collection.find({"id":precision_db['id']}).count() == 0:
        precisions_collection.insert_one(precision_db)


    return to_return



def cosineSimilarity(toAnalyze,tokenizer=True,returnFilm=True):
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

    if returnFilm:
        details_to_return = list()
        for element in ordered_array:
            details_to_return.append(film_list[element])

        return details_to_return
    else:
        return ordered_array


def cosineSimilarityReccomended(toAnalyze,tokenizer=True):
    if tokenizer:
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(toAnalyze)
    else:
        tfidf_vectorizer = TfidfVectorizer(tokenizer=lambda x: x, stop_words=None, lowercase=False)
        tfidf_matrix = tfidf_vectorizer.fit_transform(toAnalyze)
    similarity_array = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)
    similarity_array = similarity_array[0]
    similarity_array = numpy.delete(similarity_array,0)
    return similarity_array




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
    global true_labels
    genres_list = list()
    reccomended = list()
    count = 0
    for element in film_list:
        genres = list()
        reccomended_genres = list()
        for genre in element['genres']:
            genres.append(genre['name'])
            reccomended_genres.append(genre['name'])
        genres_list.append(genres)
        if count <=20:
            reccomended.append(reccomended_genres)
        count = count+1

    genres_similarity_array = cosineSimilarityReccomended(reccomended,tokenizer=False)
    genres_db = genres_collection.find()
    genres_dict = dict()
    for element in genres_db:
        indexed_documents = list()
        genres_dict[element['name']] = indexed_documents

    count = 0
    for element in genres_list:
        for genre in element:
            genres_dict[genre].append(count)
        count = count+1


    intersection = list()
    for genre in genres_list[0]:
        intersection.append(set(genres_dict[genre]))

    intersection = set.intersection(*intersection)
    intersection = list(intersection)


    details_to_return = list()
    to_return = dict()
    to_return['genresSimilarity'] = genres_similarity_array.tolist()
    if len(intersection)<=20:
        return to_return
    else:
        overviews = list()
        overviews.append(film_list[0]['overview'])
        for element in intersection:
            if element != 0:
                overviews.append(film_list[element]['overview'])
        orderedArray = cosineSimilarity(overviews,returnFilm=False)
        for element in orderedArray:
            details_to_return.append(film_list[intersection[element]])
        predicted_labels = getPredictedLabels(details_to_return)
        precision = computeConfusionMatrix(true_labels,predicted_labels,"./public/images/genres.png")
        to_return['details'] = details_to_return
        to_return['precision'] = precision
        return to_return







def getRelatedByCast():
    global film_list
    global true_labels
    cast_list = list()
    reccomended = list()
    count = 0
    for element in film_list:
        cast = list()
        reccomended_cast = list()
        for member in element['credits']['cast']:
            cast.append(member['name'])
            reccomended_cast.append(member['name'])

        cast_list.append(cast)
        if count <=20:
            reccomended.append(reccomended_cast)
        count = count + 1

    details_to_return = cosineSimilarity(cast_list,tokenizer=False)
    cast_similarity_array = cosineSimilarityReccomended(reccomended,tokenizer=False)
    predicted_labels = getPredictedLabels(details_to_return)
    precision = computeConfusionMatrix(true_labels,predicted_labels, "./public/images/cast.png")
    to_return = dict()
    to_return['details'] = details_to_return
    to_return['precision'] = precision
    to_return['castSimilarity'] = cast_similarity_array.tolist()
    return to_return




def getRelatedByCrew():
    global film_list
    global true_labels
    crew_list = list()
    reccomended = list()
    count = 0
    for element in film_list:
        crew = list()
        reccomended_crew = list()
        for member in element['credits']['crew']:
            crew.append(member['name'])
            reccomended_crew.append(member['name'])
        crew_list.append(crew)
        if count <=20:
            reccomended.append(reccomended_crew)
        count = count+1

    details_to_return = cosineSimilarity(crew_list,tokenizer=False)
    crew_similarity_array = cosineSimilarityReccomended(reccomended,tokenizer=False)
    predicted_labels = getPredictedLabels(details_to_return)
    precision = computeConfusionMatrix(true_labels,predicted_labels,"./public/images/crew.png")
    to_return = dict()
    to_return['details'] = details_to_return
    to_return['precision'] = precision
    to_return['crewSimilarity'] = crew_similarity_array.tolist()
    return to_return



def getRelatedByProductionCompanies():
    global film_list
    global true_labels
    company_list = list()
    reccomended = list()
    count = 0
    for element in film_list:
        companies = list()
        reccomended_companies = list()
        for company in element['production_companies']:
            companies.append(company['name'])
            reccomended_companies.append(company['name'])
        company_list.append(companies)
        if count <=20:
            reccomended.append(reccomended_companies)
        count = count+1

    details_to_return = cosineSimilarity(company_list,tokenizer=False)
    companies_similarity_array = cosineSimilarityReccomended(reccomended,tokenizer=False)
    predicted_labels = getPredictedLabels(details_to_return)
    precision = computeConfusionMatrix(true_labels, predicted_labels, "./public/images/production_companies.png")
    to_return = dict()
    to_return['details'] = details_to_return
    to_return['precision'] = precision
    to_return['companiesSimilarity'] = companies_similarity_array.tolist()
    return to_return


def getRelatedByGenresCosineSimilarity():
    global film_list
    global true_labels
    genres_list = list()
    for element in film_list:
        genres = list()
        for genre in element['genres']:
            genres.append(genre['name'])
        genres_list.append(genres)

    details_to_return = cosineSimilarity(genres_list, tokenizer=False)
    predicted_labels = getPredictedLabels(details_to_return)
    precision = computeConfusionMatrix(true_labels, predicted_labels, "./public/images/genres_cosine_similarity.png")
    to_return = dict()
    to_return['details'] = details_to_return
    to_return['precision'] = precision
    return to_return




