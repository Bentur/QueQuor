"""
Toutes les fonctions utiles pour l'utilisation de la bdd
"""
import sqlite3

bdd = None
cursor = None

def connect():
    """
    connection à la base de donnée
    """
    global bdd, cursor
    bdd = sqlite3.connect('data\data.db')
    cursor = bdd.cursor()

def create_bdd():
    """
    création/effacage de la bdd
    """
    print("création de la BDD")
    # creation de la table films
    global bdd, cursor
    try:
        cursor = bdd.cursor()
        try:
            cursor.execute("""
            DROP TABLE films
            """)
            bdd.commit()
        except:
            print("table inexistante")
        cursor.execute("""
    CREATE TABLE films(
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        titre TEXT,
        annee INTERGER,
        titre_vrai TEXT,
        original_title TEXT,
        collection TEXT,
        date TEXT,  
        categories TEXT,
        synopsis TEXT,
        realisateurs TEXT,
        acteurs TEXT,
        note FLOAT,
        VO TEXT,
        pays TEXT,
        adult BOOL
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


def entry_exist(titre, annee):
    #on regarde si le film est déja dans la BDD
    #return true si oui, false si non
    donnee = (titre, annee)
    cursor.execute("""
        SELECT * FROM films WHERE titre = ? and annee = ?
        """, donnee)
    return len(cursor.fetchall())>0

def add_entry(titre, annee, titre_vrai, original_title, collection, date, l_genre, synopsis, l_directeurs, l_acteurs, note, VO, pays, adult):
    """
    ajoute une entrée à la bdd
    :param titre: titre clé pour le film (sert pour retrouver le film, titre en minuscule, sas caractère spéciaux
    :param annee: annee théorique du film, pour clé retrouver le film
    :param titre_vrai: titre VF du film, selon tmdb
    :param original_title: titre VO du film, selon tmdb
    :param collection: si le film appartient à une collecion, le nom de celle ci, sinon None, selon tmdb
    :param date: date de release du film AAAA:MM:DD, selon tmdb
    :param l_genre: liste des genres du film, selon tmdb
    :param synopsis: synopsis du film, selon tmdb
    :param l_directeurs: liste des réalisateurs, selon tmdb
    :param l_acteurs: liste des acteurs, selon tmdb
    :param note: note du film, selon tmdb
    :param VO: langue VO, selon tmdb
    :param pays: pays d'origine, selon tmdb
    :param adult: True si film pour adult, selon tmdb
    """
    global bdd, cursor
    cursor.execute("""INSERT INTO films(titre, annee, titre_vrai, original_title, collection, date, categories, synopsis, realisateurs, acteurs, note, VO, pays, adult) 
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            titre, annee, titre_vrai, original_title, collection, date, str(l_genre), synopsis, str(l_directeurs), str(l_acteurs), note, VO, str(pays), adult))
    bdd.commit()

def update_entry(titre, annee, titre_vrai, original_title, collection, date, l_genre, synopsis, l_directeurs, l_acteurs, note, VO, pays, adult):
    """
    modifie une entrée de la bdd
    :param titre: titre clé pour le film (sert pour retrouver le film, titre en minuscule, sas caractère spéciaux
    :param annee: annee théorique du film, pour clé retrouver le film
    :param titre_vrai: titre VF du film, selon tmdb
    :param original_title: titre VO du film, selon tmdb
    :param collection: si le film appartient à une collecion, le nom de celle ci, sinon None, selon tmdb
    :param date: date de release du film AAAA:MM:DD, selon tmdb
    :param l_genre: liste des genres du film, selon tmdb
    :param synopsis: synopsis du film, selon tmdb
    :param l_directeurs: liste des réalisateurs, selon tmdb
    :param l_acteurs: liste des acteurs, selon tmdb
    :param note: note du film, selon tmdb
    :param VO: langue VO, selon tmdb
    :param pays: pays d'origine, selon tmdb
    :param adult: True si film pour adult, selon tmdb
    """
    cursor.execute("""UPDATE films SET titre_vrai = ?, original_title = ?, collection = ?, date = ?, categories = ?, synopsis = ?, realisateurs = ?, acteurs = ?, note = ?, VO = ?, pays = ?, adult = ?
                                            WHERE (titre == ? and annee == ?)""",
                   (titre_vrai, original_title, collection, date, l_genre, synopsis, l_directeurs, l_acteurs, note, VO, pays, adult, titre, annee))
    bdd.commit()

def get_entry(titre, annee):
    """
    recherche les informations correspondantes au film entré en paramètre
    :param titre:
    :param annee:
    """
    global cursor
    donnee = (titre, annee)
    cursor.execute(
        """SELECT titre_vrai, original_title, collection, date, categories, synopsis, realisateurs, acteurs, note, VO, pays, adult FROM films WHERE titre == ? AND annee == ?""",
        donnee)
    #print("recherche : ", titre, annee)
    try:
        titre_vrai, original_title, collection, date, categories, synopsis, realisateurs, acteurs, note, VO, pays, adult = cursor.fetchall()[0]
        #categories, realisateurs, acteurs, pays, adult = eval(categories), eval(realisateurs), eval(acteurs), eval(pays), eval(adult)
        categories, realisateurs, acteurs, pays = eval(categories), eval(realisateurs), eval(acteurs), eval(pays)

    except IndexError as er:
        print("no information about : ", titre, " ", annee)
        titre_vrai, original_title, collection, date, categories, synopsis, realisateurs, acteurs, note, VO, pays, adult = " ", " ", None, "2000-00-00", [], " ", [], [], 5, " ", [], False
    except SyntaxError as er:
        print(er)
        titre_vrai, original_title, collection, date, categories, synopsis, realisateurs, acteurs, note, VO, pays, adult = " ", " ", None, "2000-00-00", [], " ", [], [], 5, " ", [], False

    return (titre_vrai, original_title, collection, date, categories, synopsis, realisateurs, acteurs, note, VO, pays, adult)

def get_categories(titre, annee):
    global cursor
    cursor.execute("""select categories from films WHERE titre == ? AND annee == ?""", (titre, annee))
    cat = cursor.fetchone()
    return cat

def chercher_categories():
    """
    return une liste de toutes les categories de film qu'il y a dans la bdd
    """
    global cursor
    cursor.execute("""SELECT categories FROM films""")

    c = cursor.fetchall()
    l = []
    for categories in c:
        categories = eval(categories[0])
        for cat in categories:
            if(not cat in l):
                l.append(cat)
    print(l)
    return l

def close():
    global bdd
    bdd.close()
    print("closing bdd")