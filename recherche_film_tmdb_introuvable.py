import sqlite3
import numpy as np
import os
import time
import urllib.request
import re
import requests

import scan
from util import reecriture
import util_bdd as bdd
import util_tmdb


films_introuvable = np.loadtxt("data\\film_tmdb_introuvable.csv", delimiter=";", dtype=object)

bdd.connect()
#init de tmdb
util_tmdb.init_tmdb()

print(films_introuvable.shape)
for film in films_introuvable:
    if (str(films_introuvable.shape)[-2] == ","):
        print("un seul film")
        film = films_introuvable

    print("\n")
    print("Recherche : ", film)
    # on regarde si le film est déja dans la BDD
    s = reecriture(film[0])
    s = s.lower()
    film_trouve = bdd.entry_exist(s, film[1])

    if(len(film[2])>0):
        print("id valide, on fait la recherche")
        id = eval(film[2])
        titre = film[0]
        annee = film[1]
        titre_vrai, original_title, collection, date, l_genre, synopsis, note, VO, pays, adult, poster_path, backdrop_path = util_tmdb.get_infos(id)

        # téléchargement fanart et poster
        util_tmdb.download_poster_fanart(titre, annee, poster_path, backdrop_path)

        print("film trouvé : ", titre_vrai)
        l_acteurs, l_directeurs = util_tmdb.get_credits(id)

        if(not(film_trouve)):
            print("le film n'existe pas, on l'ajoute")
            # ajout de l'entrée
            bdd.add_entry(titre, annee, titre_vrai, original_title, collection, date, str(l_genre), synopsis,
                          str(l_directeurs), str(l_acteurs), note, VO, str(pays), adult)
        else :
            #modification de l'entrée
            print("le film existe, on le modifie")
            bdd.update_entry(titre, annee, titre_vrai, original_title, collection, date, str(l_genre), synopsis,
                      str(l_directeurs), str(l_acteurs), note, VO, str(pays), adult)

    else :
        print("id non valide")

    if (films_introuvable.shape[0] == 1):
        break

bdd.close()
