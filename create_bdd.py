import sqlite3
import numpy as np

def purifier_synopsis(syno):
    #liste des trucs à enlever et par quoi remplacer
    l_truc_a_enlever = [["&ampnbsp", " "], [";", ""], ["&ampquot", ""], ["&quot", ""],
                        ["&ampeacute", "é"], ["&ampagrave", "à"], ["&ampegrave", "è"],
                        ["&ampecirc", "ê"], ["&ampoelig", "oe"]]

    for truc in l_truc_a_enlever:
        l = syno.split(truc[0])
        s = ""
        for e in l:
            s+= e + truc[1]
        if(len(truc[1])>0):
            s = s[:-len(truc[1])]
        syno = s

    return syno

#creation bdd
bdd = sqlite3.connect('data\data.db')

#creation de la table films
try:
    cursor = bdd.cursor()

    try :
        cursor.execute("""
        DROP TABLE films
        """)
        bdd.commit()
    except :
        print("table inexistante")
    cursor.execute("""
CREATE TABLE films(
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    titre TEXT,
    annee INTERGER,
    categories TEXT,
    synopsis TEXT,
    realisateurs TEXT,
    acteurs TEXT,
    note FLOAT
)
""")
    bdd.commit()
except sqlite3.OperationalError:
    print('Erreur la table existe déjà')
except Exception as e:
    print("Erreur")
    bdd.rollback()
finally:
    print("table films créé")

#on place tout les films dont on connait deja les infos
film = np.loadtxt("data\\data.csv", delimiter=";", dtype = object)

for f in film:
    titre = f[0]
    annee = f[3]
    categories = f[11]
    synopsis = f[12]
    realisateurs = f[13]
    acteurs = f[14]
    note = f[15]

    #on enleve les espaces si y'en a:
    l = [eval(categories), eval(realisateurs), eval(acteurs)]
    if(len(eval(categories))>0):
        for li in l:
            for i in range(len(li)):
                while(li[i][0] == ' '):
                    li[i] = li[i][1:]
                while (li[i][-1] == " "):
                    li[i] = li[i][:-1]
        categories = l[0]
        realisateurs = l[1]
        acteurs = l[2]

        #on fait pareil pour les titres
        while(titre[0]==' '):
            titre = titre[1:]
        while(titre[-1]==' '):
            titre = titre[:-1]

        print(titre, annee, categories, realisateurs, acteurs)
        cursor = bdd.cursor()
        cursor.execute("""
        INSERT INTO films(titre, annee, categories, synopsis, realisateurs, acteurs, note) 
        VALUES(?, ?, ?, ?, ?, ?, ?)""", (titre, annee, str(categories), purifier_synopsis(synopsis), str(realisateurs), str(acteurs), note))
        bdd.commit()
#fermeture de la bdd
bdd.close()

