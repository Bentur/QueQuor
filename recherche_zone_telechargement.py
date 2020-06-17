# -*- coding: utf-8 -*-

import numpy as np
import os
import time
import urllib.request
import re
import requests
from bs4 import BeautifulSoup
import socket


page  = ""

page_erreur = []

def getInformationFromZoneTelechargement(i):
    global page
    """
    :param i: le numéro de la page
    :return: de la soupe
    """
    if(i == 1):
        #https://www2.zone-telechargement4.vip/hdlight-1080/
        #https://www.zone-telechargement.group/hdlight-1080/
        url = "https://www2.zone-telechargement4.vip/hdlight-1080/"
    else :
        url = "https://www2.zone-telechargement4.vip/hdlight-1080/page/" + str(i) + "/"

    print(url)

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    head = {'User-Agent': user_agent,
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

    try :
        rep = urllib.request.Request(url, None, head)
        page = urllib.request.urlopen(rep, timeout=5)
    except urllib.error.HTTPError as e:
        print(e)
        return None
    except urllib.error.URLError  as e:
        print(e)
        return None

    except socket.timeout as e:
        print(e)
        return None

    """
    requete = requests.get(url, headers=head)
    page = requete.content
    print(page)
    """
    soup = BeautifulSoup(page, "html.parser")

    #h1 = soup.find('script', {"type": "application/ld+json"})
    #h1 = soup.find( class="mov-t nowrap")
    #return soup
    #a = soup.find_all('div', {"class":"mov clearfix"})

    return soup

def traiter_informations(soup):
    if(soup == None):
        return [("zzzzbug", "bug", "bug", "bug")]
    """
    :param a: de la soupe
    :return: une list : [titre,  année, langue, lien]
    """
    langues = []


    lang = soup.find_all('span', attrs={"class":"langue"})
    for lan in lang:
        langues.append(lan.text.strip())

    #année et titre
    ans = []
    titres = []

    """
    a = soup.find_all('div', attrs={"class":"mov-ms"})
    #for i in range(0, len(c)-1, 2):
    for c in list(a):
        b = c.find('a').text.strip()
        ans.append(b[:4])
    """

    #lien
    links = []
    a = soup.find_all('div', attrs={"class": "mov clearfix"})
    for l in list(a):
        li = l.find('a').get("href")
        if(not(li in links)):
            links.append(li)
            b = l.find('a').text.strip()
            ans.append(b[:4])

            fin = li.split('/')[-1][:-5]
            l_t = fin.split("-")
            #langue = l_t[-1]

            titre = ""
            for i in range(1, len(l_t) - 2):
                titre += l_t[i] + " "
            titres.append(titre[:-1])

    """
    print(titres)
    print(langues)
    print(ans)
    print(links)
    """
    RE = []

    for i in range(len(titres)):
        RE.append((titres[i], ans[i], langues[i], links[i]))

    """
    for link in a:
        # liens
        b = link.get('href')
        if (not (b in r)):
            r.append(b)
            # annee
            c = link.find('div', {"class": "mov-ms"})
            #print(c)
            # <div class="mov-ms"><a href="https://www.zone-telechargement2.vip/xfsearch/annee-de-sortie/2010/">2010</a></div>
            # y'a pus qu'à se servir
            annee = str(c).split("annee-de-sortie")[1].split("/")  # yolo
            an.append(annee[1])

    R = []
    for link in r:
        lien = link

        fin = link.split('/')[-1][:-5]
        l_t = fin.split("-")
        langue = l_t[-1]

        titre = ""
        for i in range(1, len(l_t) - 2):
            titre += l_t[i] + " "
        titre = titre[:-1]
        R.append((titre, langue, lien))

    RE = []
    for i in range(len(R)):
        r = R[i]
        a = an[i]
        #print(r, a)

        RE.append((r[0], a, r[1], r[2]))
    """
    return RE

def cherche_medor(debut, fin):
    """
    vas chercher medor, va chercher !!!
    c'est un bon chien ça <3
    :param debut: à quelle page on commence la recherche
    :param fin: à quelle page on fini la recherche (inclus)
    :return: une liste avec tous les films disponible
    """

    L = []
    for i in range(debut, fin+1):
        print("récupération de la page : ", i)
        a = getInformationFromZoneTelechargement(i)

        b = traiter_informations(a)
        print(b)
        print(len(b), " films ajoutés\n")
        L += b


        if(len(b)!=28):
            page_erreur.append((i, len(b)))

        if(len(b) == 1):
            break
        time.sleep(3) #on évite de surcharger le serveur, quand même

    return L


#soup = getInformationFromZoneTelechargement(1)
#soup2 = getInformationFromZoneTelechargement(2)

L = cherche_medor(1, 20)

data = np.loadtxt('data\\film_zone_telechargement.csv', delimiter=";", dtype = str, encoding='utf-8')
#film_trouvable = np.loadtxt('data\\film_zone_telechargement.csv', fmt="%s", delimiter=";")

films = np.array(L, dtype=str)

#concaténation des tableaux
#film_trouvable = data
film_trouvable = np.vstack((data, films))

#remove duplicate
film_trouvable = np.unique(film_trouvable, axis=0)

#tri
film_trouvable = film_trouvable[film_trouvable[:, 0].argsort()]

f = list(film_trouvable)
F = []

def traiter_langue(langue):
    if(langue[0] == "("):
        langue = langue[1:]
    if(langue[-1] == ")"):
        langue = langue[:-1]

    return langue[0].upper() + langue[1:].lower()

l_langues = ["Multi", "Vo", "Vostfr", "Truefrench", "French", "Vfq"]
i = 0
while i < len(f):
    titre = f[i][0]
    annee = f[i][1]
    lan = traiter_langue(f[i][2])
    lien = f[i][3]

    if(titre == "" or annee == "" or annee == "bug"):
        i+=1
    else :
        n = 1 #nb d'occurence du film
        while(i+n<len(f)):
            if(f[i+n][0] == titre and f[i+n][1] == annee):
                n+=1
            else:
                break

        #on cherche l'occurence qui nous plait
        k = 0
        for j in range(n):
            langue_bien = traiter_langue(f[i+k][2])
            langue_test = traiter_langue(f[i+j][2])
            try:
                if(l_langues.index(langue_bien)>l_langues.index(langue_test)):
                    k=j
            except:
                print("langue non connue : ", langue_test)

        F.append((titre, annee, traiter_langue(f[i+k][2]), f[i+k][3]))
        i+=n



#écriture
while True:
    try :
        np.savetxt('data\\film_zone_telechargement.csv', np.array(F), fmt="%s", delimiter=";")
        break
    except PermissionError as e:
        print(e)
        print("veillez fermer le fichier film_rone_telechargement.csv\n")
        time.sleep(2)

print("films trouvable placés dans le fichier film_zone_telechargement.csv")

print("nombre d'erreur : ", len(page_erreur), " ", page_erreur)


"""
j = np.array(film_nope)

<a class="mov-t nowrap" href="https://www.zone-telechargement2.vip/films-gratuit/520994-une-vie-de-chat-HDLight 1080p-French.html"> <div class="mov-i img-box" data-content="Dino est un chat qui partage sa vie entre deux maisons. Le jour, il vit avec Zoé, la fillette d’une commissaire de police. La nuit, il escalade les toits de Paris en compagnie de Nico, un cambrioleur d’une grande habileté. Jeanne, la commissaire de police, est sur les dents. Elle doit à la fo..." data-html="true" data-toggle="popover" data-trigger="hover" title="Une vie de chat">
<img alt="Une vie de chat" height="320px" src="/uploads/posts/2020-01/thumbs/une-vie-de-chat5e2fb366882b6.jpg" title="Une vie de chat" width="200px"/>
<div class="mov-mask flex-col ps-link" data-link="https://www.zone-telechargement2.vip/films-gratuit/520994-une-vie-de-chat-HDLight 1080p-French.html"></div>
<div class="mov-ms"><a href="https://www.zone-telechargement2.vip/xfsearch/annee-de-sortie/2010/">2010</a></div>
<div class="mov-left">
<span class="badge badge-warning">NEW</span>
</div>
</div>
</a>

<a class="mov-t nowrap" href="https://www.zone-telechargement2.vip/films-gratuit/520994-une-vie-de-chat-HDLight 1080p-French.html"> Une vie de chat</a>
"""