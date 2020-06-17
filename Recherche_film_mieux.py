"""
recherche les films disponible en meilleur qualité que ce qu'on a déja

scan les fichier comme d'hab
nécessite d'avoir préalablement lancer recher_film_zone_telechargement pour récuperer les films dispo

ouvre donc le fichier data/film_zone_telechargement.csv

"""

import numpy as np
from difflib import SequenceMatcher
import time

from util import reecriture
import scan

#[titre, annee, titre_an, serie, langue, qualite, info, path]
films = np.array(scan.scan_all_films(), dtype=object)

qualite_acceptable = ["1080p"]
langue_acceptable = ["French", "Multi"]
l_langues = ["Multi", "Vo", "Vostfr", "French", "Truefrench", "Vff", "Vf", "Vfi", "French voq", "Vfq"]

data = np.loadtxt('data\\film_zone_telechargement.csv', delimiter=";", dtype = str, encoding='utf-8')

def tester_film(titre_film1, annee1, titre_film2, annee2):
    """
    test si 2 films sont possiblement les même
    :param titre_film1:
    :param annee1:
    :param titre_film2:
    :param annee2:
    :return: true si oui, false sinon
    """
    # on test si l'année convient
    if(abs(annee2 - annee1) < 2):
        # on test si le titre est presque le même (français ou anglais)
        print(titre_film2, titre_film1, SequenceMatcher(a=titre_film2, b=titre_film1).ratio())
        if (titre_film1 in titre_film2 or titre_film2 in titre_film1):
            return True
        elif (SequenceMatcher(a=titre_film2, b=titre_film1).ratio() > 0.7):
            return True

    return False

def ajout_film(film):
    titre = reecriture(film[0]).lower()
    lan = film[4][0].upper() + film[4][1:].lower()
    if("vfq" in lan): #and not("vff")):
        lan = "Vfq"
    if("Multi" in lan):
        lan = "Multi"

    if(lan == "Vf"):
        lan = "French"

    if(lan == "Vff"):
        lan = "Truefrench"
    a = (titre, int(film[1]), lan, film[5])
    film_nope.append(a)


#récupération de tous les films qui n'ont pas une qualié acceptable
#par définition, les films français ont commme langue French et les films traduis en français VF
film_nope = []
for film in films:
    qual = film[5]
    langue = film[4]
    info = film[6]
    if(not(qual in qualite_acceptable)):
        pass
        ajout_film(film[:-1])
    elif(not(langue in langue_acceptable)):
        if "Multi" in langue :
            l = langue.split(" ")
            L = []
            for e in l:
                L += e.split("-")
            L = l[1:]

            if("VFQ" in L):
                a = ["VF, VFF, VFI"]
                flag = False
                for e in a:
                    for f in L:
                        flag |= e == f
                if(not(flag)):
                    ajout_film(film[:-1])
        else:
            ajout_film(film[:-1])

print(film_nope)
o = np.array(film_nope)

#réecriture des noms des films de data pour pouvoir faire le traitement:
film_disponible = []
for film in list(data):
    titre = reecriture(film[0]).lower()
    qual = film[2]
    a = (titre, int(film[1]), qual, film[3])
    film_disponible.append(a)

def recherche(titre, annee):
    """
    recherche dichotomique pour trouver une correspondance
    :param titre:
    :param annee:
    :return:
    """
    a = 0
    b = len(film_disponible) - 1
    m = (a + b) // 2
    #print("\ndébut de la dichotomie : ")
    while a < b:
        #print("\na : ", a, ", b : ", b, ", m : ", m)
        #test d'égalité
        titre2 = film_disponible[m][0]
        annee2 = film_disponible[m][1]

        #print("test des films : ", titre, annee, titre2, annee2)

        if tester_film(titre, annee, titre2, annee2):
            print("________________film trouvé : ", titre, annee, titre2, annee2)
            return m
        elif titre2 > titre:
            b = m - 1
        else:
            a = m + 1
        m = (a + b) // 2

    titre2 = film_disponible[m][0]
    annee2 = film_disponible[m][1]

    #print("test des films : ", titre, annee, titre2, annee2)

    if tester_film(titre, annee, titre2, annee2):
        print("________________film trouvé : ", titre, annee, titre2, annee2)
        return m

    return None

film_a_telecharger = []
#on parcours tous les films nope pour trouver une correspondance
#on va faire un algorithme dichotomique, faut savoir prendre des risques

for film_nul in film_nope:
    #on regarde si il y a des matchs avec le titre:
    print("\n__________________________________________________________________________________________\n")
    titre = film_nul[0]
    annee = film_nul[1]
    lan = film_nul[2]
    match = recherche(titre, annee)
    if(match != None):
        print("trouver un matche entre : ", titre, annee, " et : ", film_disponible[match][0], film_disponible[match][1])
        #print(film_disponible[match][2], lan)
        #print(l_langues.index(film_disponible[match][2]), l_langues.index(lan))
        if (l_langues.index(film_disponible[match][2]) < l_langues.index(lan)):
            print("La langue est mieux : ", lan, "->", film_disponible[match][2])
            film_a_telecharger.append((titre, annee, lan, film_disponible[match][2], film_disponible[match][3]))
        elif (not(film_nul[3] in qualite_acceptable)):
            print("la qualitée est mieux : ", film_nul[3], "-> 1080p")
            film_a_telecharger.append((titre, annee, film_nul[3], "1080p", film_disponible[match][3]))

    else:
        print("pas de match pour : ", titre, annee, lan)

b = np.array(film_a_telecharger)
print(film_a_telecharger)

print("\n||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
print("\nIl y a", len(film_nope), "films qui ne sont pas à leur top, nous avons trouvé", len(film_a_telecharger), "films mieux")
print("y'a pus qu'à télécharger comme un porc")

#écriture
while True:
    try :
        np.savetxt('data\\film_a_telecharger.csv', b, fmt="%s", delimiter=";")
        break
    except PermissionError as e:
        print(e)
        print("veillez fermer le fichier film_a_telecharger.csv\n")
        time.sleep(2)

#écriture
while True:
    try :
        np.savetxt('data\\film_nope.csv', np.array(film_nope), fmt="%s", delimiter=";")
        break
    except PermissionError as e:
        print(e)
        print("veillez fermer le fichier film_nope.csv\n")
        time.sleep(2)