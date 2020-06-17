"""
fonction ayant lien avec tmdb
"""

from tmdbv3api import TMDb, Movie, TV, Season, Person, Discover
import urllib.request
import time

from difflib import SequenceMatcher
import re

from util import reecriture

movie = None
tmdb = None

def init_tmdb():
    """
    init tmdb, obligatoire avant de commencer
    """
    global movie, tmdb
    tmdb = TMDb()
    tmdb.api_key = '5a1bff6741409f453efe0f46b4be60b9'
    tmdb.language = 'fr'
    movie = Movie()

def search(titre):
    global movie
    return movie.search(titre)

def details(id):
    global movie
    return movie.details(id)

def get_id_from_google(titre, annee):
    """
    demande à google de faire la recherche sur the movie database
    :param titre:
    :param annee:
    :return: la liste des id tmdb correspondant
    """
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    headers = {'User-Agent': user_agent,
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

    ext = "fr"
    lang = "fr"  # sur quel datacenter chercher?"

    keyword = 'the+movie+db+'
    for mot in titre.split(" "):
        keyword += reecriture(mot) + "+"
    keyword += str(annee)
    # keyword += '+google.com'  # Mot clé cherché

    pagenum = 0  # on commence à la page 1
    googlefrurl = "http://www.google." + ext + "/custom?hl=" + lang + "&q=" + keyword + "&start=" + str(pagenum)

    try:
        rep = urllib.request.Request(googlefrurl, None, headers)
        response = urllib.request.urlopen(rep)
        result = str(response.read())
    except urllib.error.HTTPError as er:
        print(er)
        return None

    sep = '<a href=.*?>'
    matches = re.findall(sep, result)
    res_tab = []
    for elt in matches:
        if (("themoviedb.org/movie/" in elt)):
            sep = 'http.*?"'
            match = re.findall(sep, elt)

            try :
                a = match[0][:-1]
                a = a.split('/')[-1]
                a = a.split('-')[0]
                a = eval(a)
                if(not(a in res_tab)):
                    res_tab.append(a)
            except:
                pass
                #print("Petite erreur avec Google, mais tout va bien")
            if (len(res_tab) > 5):
                break

    return res_tab

def tester_film(titre_film1, titre_VO1, annee1, titre_film2, titre_VO2, annee2):
    """
    test si 2 films sont possiblement les même
    :param titre_film1:
    :param titre_VO1:
    :param annee1:
    :param titre_film2:
    :param titre_VO2:
    :param annee2:
    :return: true si oui, false sinon
    """
    # on test si l'année convient
    if(abs(annee2 - annee1) < 2):
        print(annee1, annee2)
        # on test si le titre est presque le même (français ou anglais)
        print(titre_film2, titre_film1, SequenceMatcher(a=titre_film2, b=titre_film1).ratio())
        if (titre_film1 in titre_film2 or titre_film2 in titre_film1):
            return True
        elif (SequenceMatcher(a=titre_film2, b=titre_film1).ratio() > 0.7):
            return True
        # on test le titre vo si il existe
        elif(len(titre_VO1) > 0):
            titre_VO1 = reecriture(titre_VO1).lower()
            sq = SequenceMatcher(a=titre_film2, b=titre_VO1).ratio()
            print("test du nom VO : ", titre_film2, titre_VO1, sq)
            if (sq > 0.7):
                return True
        elif (SequenceMatcher(a=titre_VO2, b=titre_film1).ratio() > 0.7):
            return True
    return False

def download_poster_fanart(titre, annee, path_poster, path_fanart):
    """
    download fanart et poster et les enegistre avec nom = titre + annee + .jpg
    :param titre: titre clé du film (minuscules et pas de caractère spéciaux
    :param annee: anne clé du film
    :param path_poster: chemin relatif pour télécharger le poster
    :param path_fanart: chemin relatif pour télécharger le fanart
    """
    #poster
    path_p = "data\\poster\\" + str(titre) + " " + str(annee) + ".jpg"
    try:
        urllib.request.urlretrieve("https://image.tmdb.org/t/p/w300_and_h450_bestv2" + path_poster, path_p)
        time.sleep(0.1)
    except:
        print("Couldn't find poster for : ")
        print(titre + '.jpg\n')

    # fanart
    path_f = "data\\fanart\\" + str(titre)  + " " + str(annee) + ".jpg"
    try:
        urllib.request.urlretrieve("https://image.tmdb.org/t/p/original" + path_fanart, path_f)
        time.sleep(0.1)
    except:
        print("Couldn't find fanart for : ")
        print(titre + '.jpg\n')

def get_infos(id):
    """
    :param id: id du film
    :return: [Titre_VF, Titre_VO, Titre_série, Année, Categories, Synopsis, note, Pays]
    """
    global movie

    film = movie.details(id)

    adult = film.adult
    collection = film.belongs_to_collection
    if(collection != None):
        collection = collection["name"]
    l_genre = []
    for genre in film.genres:
        l_genre.append(genre["name"])

    original_title = film.original_title
    synopsis = film.overview
    note = film.vote_average
    titre = film.title
    VO = film.original_language
    pays = []
    for country in film.production_countries:
        pays.append(country["name"])
    date = film.release_date

    return (titre, original_title, collection, date, l_genre, synopsis, note, VO, pays, adult, film.poster_path, film.backdrop_path)


def get_credits(id):
    """
    :param id: id du film
    :return: la liste des acteurs, pour chaque acteur : on récupère une liste avec [name, character}
            la liste des réalisateurs
    """
    global movie

    cred = movie.credits(id)
    dic = dict(cred.entries)

    id = dic.get("id")
    casts = dic.get("cast")
    crews = dic.get("crew")

    l_acteurs = []
    for cast in casts:
        d = dict(cast)
        if (d.get("profile_path") == None or int(d.get("order")) > 10):
            break

        l_acteurs.append([d.get("name"), d.get("character")])
        #print("Acteur : ", d.get("name"), " | Rôle : ", d.get("character"), " | Genre : ", d.get("gender"))

    l_directeurs = []
    for crew in crews:
        d = dict(crew)
        if(d.get("department") == "Directing"):
            l_directeurs.append(d.get("name"))
        #print(d)

    return (l_acteurs, l_directeurs)