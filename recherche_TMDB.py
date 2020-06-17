"""
recherche les infos sur les films/séries à partir de The Movie Database api
api key : 5a1bff6741409f453efe0f46b4be60b9
Example API Request : https://api.themoviedb.org/3/movie/550?api_key=5a1bff6741409f453efe0f46b4be60b9
API Read Access Token (v4 auth) : eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1YTFiZmY2NzQxNDA5ZjQ1M2VmZTBmNDZiNGJlNjBiOSIsInN1YiI6IjVkZWY4MjdhY2U0ZGRjMDAxODYxZDRkMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.6lk3uXFki7pTCLWwzVDJiwNcTiW7G8LKyJgqxX3Fqa8

"""

import time
import os
import numpy as np

import scan, scan_reseau
from util import reecriture
import util_bdd as bdd
import util_tmdb

#recherche de tous les films qu'il y a sur le DD (chemin spécifié dans path_scan.txt)
t0 = time.time()
films = scan.scan_all_films()
print("\n")
print("scan time : ", time.time() - t0, '\n')

"""
#recherche réseau
films_reseau = scan_reseau.scan_all_reseau()
films += films_reseau
"""

#connexion à la BDD
bdd.connect()

#init de tmdb
util_tmdb.init_tmdb()

l_film_introuvable = []
a = 0
for film in films :

    #on regarde si le film est déja dans la BDD
    s = reecriture(film[0])
    s = s.lower()
    film_trouve = bdd.entry_exist(s, film[1])

    if(not(film_trouve)):
        print("\nfilm non trouvé : " +  str((s, film[1])))

        #on ajoute l'entrée à la BDD
        titre = reecriture(film[0])
        titre = titre.lower()
        annee = film[1]

        #recherche The Movie Database
        search = util_tmdb.search(film[0])
        res_id = None
        for resultat in search:
            print(resultat)
            try :
                trouve = util_tmdb.tester_film(titre, film[2], annee, reecriture(resultat.title).lower(),reecriture(resultat.original_title).lower(), int(resultat.release_date[:4]))
                if(trouve):
                    res_id = resultat.id
                    break
            except AttributeError as er:
                print(er)
            except ValueError as er :
                print(er)

        if(res_id == None):
            #on teste les résultats de google
            print("Recherche avec google")
            l_id = util_tmdb.get_id_from_google(film[0], film[1])
            print("petit delay")
            print("nombres de résultats : ", len(l_id))
            time.sleep(5)
            for id in l_id :
                resultat = util_tmdb.details(id)
                print(resultat.title)
                try :
                    trouve = util_tmdb.tester_film(titre, film[2], annee, reecriture(resultat.title).lower(), reecriture(resultat.original_title).lower(), int(resultat.release_date[:4]))
                    if (trouve):
                        res_id = id
                        break
                except AttributeError as er:
                    print(er)
                except ValueError as er:
                    print(er)

        if(res_id == None):
            print("_______film non trouvé : ", film[0])
            l_film_introuvable.append((titre, annee))
        else :
            id = res_id
            titre_vrai, original_title, collection, date, l_genre, synopsis, note, VO, pays, adult, poster_path, backdrop_path = util_tmdb.get_infos(id)

            # téléchargement fanart et poster
            util_tmdb.download_poster_fanart(titre, annee, poster_path, backdrop_path)

            print("film trouvé : ", titre_vrai)
            l_acteurs, l_directeurs = util_tmdb.get_credits(id)

            print("ajout de l'entrée dans la bdd")
            bdd.add_entry(titre, annee, titre_vrai, original_title, collection, date, str(l_genre), synopsis, str(l_directeurs), str(l_acteurs), note, VO, str(pays), adult)

        delays = np.linspace(0, 2)
        delay = np.random.choice(delays)
        print("delay : " + str(0.5 + delay) )
        time.sleep(0.5 + delay)

bdd.close()
film_introuvable = np.array(l_film_introuvable, dtype=object)
np.savetxt('data\\film_tmdb_introuvable.csv', film_introuvable, fmt="%s", delimiter=";")

print(len(l_film_introuvable), " films introuvables placés dans le fichier film_tmdb_introuvable.csv")

print("Fin du bordel, salut")