import sys
from PyQt5.QtWidgets import QDesktopWidget, QStyle, QComboBox, QStyleOptionButton, QProxyStyle, QLineEdit, QAbstractItemView, QLabel, qApp, QStyleFactory, QMainWindow, QPushButton, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QHBoxLayout, QVBoxLayout, QGridLayout, QTextEdit
from PyQt5.QtGui import QIcon, QTextDocument, QFont, QPixmap, QColor, QImage, QPainter, QPalette, QPainterPath, QBrush, QPen, QPolygon
from PyQt5.QtCore import pyqtSlot, QSize, Qt, QPoint, QRect
import numpy as np
#import time
#import os
import subprocess as sp
import enzyme

import scan, scan_reseau
from util import reecriture, traduire_pays, colormap
import util_bdd as bdd
#import util_tmdb
from interface_popup import Popup_escape, Popup_source, Popup_categories

#https://ceg.developpez.com/tutoriels/pyqt/qt-quick-python/01-interfaces-simples/
#https://ceg.developpez.com/tutoriels/pyqt/qt-quick-python/02-interaction-qml-python/
#https://ceg.developpez.com/tutoriels/pyqt/qt-quick-python/03-programme-complet/
#http://pyqt.sourceforge.net/Docs/PyQt5/qml.html

class BaseStyle(QProxyStyle):

    def polish(self, App):
        base = QColor(255, 255, 245) #jaune pale
        side = QColor(117, 19, 107) #violet
        highlight = QColor(255, 255, 100) #jaune

        palette = QPalette(base)

        #cf : https://doc.qt.io/qt-5/qpalette.html#ColorRole-enum, enum QPalette::ColorRole

        palette.setBrush(QPalette.Highlight, highlight)
        palette.setBrush(QPalette.Text, Qt.black)
        palette.setBrush(QPalette.HighlightedText, Qt.black)
        palette.setBrush(QPalette.BrightText, Qt.red)

        #palette.setBrush(QPalette.Background, Qt.red)
        palette.setBrush(QPalette.Base, Qt.white)
        #palette.setBrush(QPalette.AlternateBase, side)
        App.setPalette(palette)

class Main():

    def __init__(self):
        #on scan à la recherche des films
        #film : [titre, annee, titre_an, serie, langue, qualite, info, path]

        #création de la bdd
        self.bdd = bdd.connect()

        #doit-on chercher les films sur le NAS ?
        self.should_search_upnp = False

        # on garde en mémoire les sources potentielles
        self.Kword = ""
        self.update_sources()

        #création de la fenêtre
        app = QApplication(sys.argv)
        app.setStyle(QStyleFactory.create('Fusion'))

        ex = App(self)

        sys.exit(app.exec_())
        bdd.close()

    def update_sources(self):
        """
        update les sources à partir du fichier
        :return:
        """

        #si True, alors on scannera la source, sinon False
        sources = scan.get_sources_films()
        self.sources = []
        for s in sources:
            if (s[-1] == '\n'):
                s = s[:-1]
            #on vérifie que la source est valide
            if(scan.verify_source(s)):
                print("__chemin source valide :", s)
                self.sources.append([s, True])
            else:
                self.sources.append([s, False])


        self.update_films()

    def update_films(self):
        """
        recharge les sources
        """
        F = []
        for s in self.sources:
            if(s[1]):
                F += scan.scanner_films(s[0])

        #scan le réseau
        if(self.should_search_upnp):
            films_reseau = scan_reseau.scan_all_reseau()
            F += films_reseau

        films = np.array(F)
        films = films[films[:, 0].argsort()]
        print("Nombre de films trouvés : ", films.shape[0])
        self.films = films[films[:, 3].argsort(kind='mergesort')]
        self.film_selected = 0
        self.selection_films = self.films
        print("Nombre de films trouvés : ", films.shape[0])

        self.update_categories()

    def update_categories(self):
        self.categories = bdd.chercher_categories()
        self.categories_selected = self.categories.copy()
        self.update_selection()

    def update_selection(self, Kword = None):
        """
        recharge la selection de film en fonction du keyword de la barre de recherche
        :param Kword: le mot entré dans la barre de recherche
        :return:
        """
        if(Kword != None):
            self.Kword = Kword.lower()

        Kword = self.Kword
        Kwords = []
        for K in Kword.split(" "):
            Kwords.append(reecriture(K))
        selection = []
        for film in self.films:
            #print("\n", film[0])
            film_ok = True

            if Kword == "":
                film_ok = True
            else :
                fs = []
                for f in film[0].split(" "):
                    fs.append(reecriture(f).lower())

                for w in Kwords:
                    flag = False
                    for wor in fs:
                        flag |= w in wor
                    film_ok &= flag

            if(film_ok):
                film_ok = False
                cat = bdd.get_categories(reecriture(film[0]).lower(), film[1])
                if not(cat == None) :
                    cat = eval(cat[0])
                    #matching categories
                    for c in cat:
                        film_ok |=  c in self.categories_selected

                    if(len(cat) == 0):
                        print("Pas d'infos pour le film : ", reecriture(film[0]).lower(), film[1])
                        film_ok = True
                else:
                    #pas d'info sur le film, donc on va dire qu'il est ok
                    print("Pas d'infos pour le film : ", reecriture(film[0]).lower(), film[1])
                    film_ok = True
            if(film_ok):
                selection.append(film)

            else:
                pass
                #print("film non ok : ", film)

        #si aucun film ne match la recherche, on met un film vide
        if(len(selection) == 0):
            selection.append(["Aucun film Trouvé", " ", " ", " ", " ", " ", " ", " ",
                     " ", " ", " ", [], " ", [], [], " ", " "])

        print("avant selection : ", len(selection))
        self.selection_films = np.array(selection, dtype=object)
        print("apres : ", self.selection_films.shape)

class App(QMainWindow):

    def __init__(self, main):
        super().__init__()

        self.x = 0.

        self.main = main
        #self.title = "Qu'es-ce qu'on regarde ?"
        desktop = QDesktopWidget()

        self.left = 0
        self.top = 0

        self.height = desktop.height()
        self.width = int(desktop.height()*1024.0/768.0)

        #print(self.width, self.height)

        style = BaseStyle()
        self.setStyle(style)
        #self.setWindowTitle(self.title)

        #pile des popups, dernier arrivé, premier sorti lors d'un appuie sur echape
        self.popup_pile = []

        self.initUI()
        self.setGeometry(self.left, self.top, self.width, self.height)
        #self.setGeometry(int(self.left + self.width/2), self.top, int(self.width/2), self.height)

        self.setMinimumWidth(int(self.width/2))

        self.setFixedHeight(self.height)
        self.setStyleSheet(StyleSheet)

        self.setWindowFlags(Qt.FramelessWindowHint);

        self.popup_escape = Popup_escape(main, self)
        self.popup_source = Popup_source(main, self)
        self.popup_categories = Popup_categories(main, self)

        self.show()

    def initUI(self):

        layout_gauche = QVBoxLayout()

        self.table_width = 300
            #recherche zone
        self.zoneRecherche = QLineEdit(self)
        self.zoneRecherche.setFixedWidth(self.table_width)
        self.zoneRecherche.setText("Recherche...")
        self.zoneRecherche.textChanged.connect(self.on_zone_recherche_text_changed)
        layout_gauche.addWidget(self.zoneRecherche)

            #tableau des films
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("Titre du Film"))
        self.tableWidget.itemClicked.connect(self.on_table_click)
        self.tableWidget.doubleClicked.connect(self.on_table_double_click)
        self.tableWidget.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers) #rends la table read only
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection) #empeche la selection multiple dans la table
        self.tableWidget.setFixedWidth(self.table_width)
        self.tableWidget.setColumnWidth(0, self.table_width)
        self.updateTableWidget(self.main.films)
        layout_gauche.addWidget(self.tableWidget)

            #les labels
        font_desc = QFont("Times", 14)

        layout_droit = QVBoxLayout() #contient : titre_annee | description_synopsis_note_fanart | affiches

        layout_titre_logo = QHBoxLayout()

        self.label_titre_annee = QLabel(self)
        self.label_titre_annee.setFont(QFont("Times", 24))
        self.label_titre_annee.setMinimumWidth(self.width)
        layout_titre_logo.addWidget(self.label_titre_annee)

        self.label_logo_qualite = QLabel(self)
        layout_titre_logo.addWidget(self.label_logo_qualite)

        layout_droit.addLayout(layout_titre_logo)

        layout_milieu_droit = QHBoxLayout()#contient : layout_description syno
        layout_description = QHBoxLayout()#contient : desc_droit desc_gauche/note

        self.label_description_gauche = QTextEdit(self)
        self.label_description_gauche.setReadOnly(True)
        self.label_description_gauche.setFont(font_desc)
        self.label_description_gauche.setFixedWidth(350)
        self.label_description_gauche.setFixedHeight(300)
        layout_description.addWidget(self.label_description_gauche)

        layou_desc_droit_note = QVBoxLayout() #contient : desc_droit note

        self.label_description_droit = QTextEdit(self)
        self.label_description_droit.setReadOnly(True)
        self.label_description_droit.setFont(font_desc)
        self.label_description_droit.setFixedWidth(350)
        self.label_description_droit.setFixedHeight(250)
        layou_desc_droit_note.addWidget(self.label_description_droit)

        self.painter = QPainter()
        self.widget_note = QWidget()
        self.widget_note.setFixedHeight(40)
        self.current_note = 10 #pour pas que ça bug faut initialiser
        self.widget_note.paintEvent = self.draw_widget_note
        layou_desc_droit_note.addWidget(self.widget_note)

        layout_description.addLayout(layou_desc_droit_note)

        layout_desc_syno = QVBoxLayout()

        self.label_synopsis = QTextEdit(self)
        self.label_synopsis.setReadOnly(True)
        self.label_synopsis.setFont(font_desc)
        self.label_synopsis.setFixedWidth(710)
        self.label_synopsis.setFixedHeight(190)

        layout_desc_syno.addLayout(layout_description)
        layout_desc_syno.addWidget(self.label_synopsis)

        layout_milieu_droit.addLayout(layout_desc_syno)

        self.label_fanart = QLabel(self)
        self.updateFanart()
        self.label_fanart.setFixedHeight(500)
        self.label_fanart.setMinimumWidth(500)
        self.label_fanart.setAlignment(Qt.AlignCenter)
        layout_milieu_droit.addWidget(self.label_fanart)

        layout_droit.addLayout(layout_milieu_droit)

        self.widget_affiches = QWidget(self)
        self.widget_affiches.paintEvent = self.draw_widget_affiche
        self.widget_affiches.setFixedHeight(410)
        self.widget_affiches.setFixedWidth(1600)
        nb_affiche = 13

        #affiche du mileu
        affiche_height = 300
        affiche_width = 200

        xoffset = self.widget_affiches.width() / 2 #- affiche_width / 2
        yoffset = 100
        self.l_affiche_gauche = []
        self.l_affiche_droit = []
        R = 600 #distance/2 entre les 2 affiches les plus éloignées
        for i in range(nb_affiche//2+1, 0, -1):
            current_affiche_heigth = affiche_height - 30*abs(i)
            current_affiche_width = int(current_affiche_heigth*2.0/3.0)

            label_affiche_gauche = QLabel(self.widget_affiches)
            label_affiche_gauche.setAlignment(Qt.AlignCenter)
            label_affiche_gauche.setFixedHeight(current_affiche_heigth)
            label_affiche_gauche.setFixedWidth(current_affiche_width)
            label_affiche_gauche.move(int(xoffset - R*np.sin(np.pi*i/(2*(nb_affiche//2+2)))) - int(current_affiche_width/2), yoffset-i*11)
            self.l_affiche_gauche.append(label_affiche_gauche)

            label_affiche_droit = QLabel(self.widget_affiches)
            label_affiche_droit.setAlignment(Qt.AlignCenter)
            label_affiche_droit.setFixedHeight(current_affiche_heigth)
            label_affiche_droit.setFixedWidth(current_affiche_width)
            label_affiche_droit.move(int(xoffset + R*np.sin(np.pi*i/(2*(nb_affiche//2+2)))) - int(current_affiche_width/2), yoffset-i*11)
            self.l_affiche_droit = [label_affiche_droit] + self.l_affiche_droit

        label_affiche = QLabel(self.widget_affiches)
        label_affiche.setAlignment(Qt.AlignCenter)
        label_affiche.setFixedHeight(affiche_height)
        label_affiche.setFixedWidth(affiche_width)
        label_affiche.move(int(xoffset) - int(affiche_width/2), int(yoffset))
        self.l_affiche = self.l_affiche_gauche + [label_affiche] + self.l_affiche_droit
        self.updateAffiche()

        layout_droit.addWidget(self.widget_affiches)

        #les boutons du bas maintenant
        layout_button = QHBoxLayout()
        button_height = 40

        self.button_lecture = QPushButton(self)
        self.button_lecture.clicked.connect(self.quit)
        self.button_lecture.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_lecture_alphabet.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_lecture.setIcon(QIcon(pixmap))
        self.button_lecture.setIconSize(pixmap.rect().size())
        self.button_lecture.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_lecture)

        self.button_night_mode = QPushButton(self)
        self.button_night_mode.clicked.connect(self.quit)
        self.button_night_mode.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_night_mode_activated.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_night_mode.setIcon(QIcon(pixmap))
        self.button_night_mode.setIconSize(pixmap.rect().size())
        self.button_night_mode.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_night_mode)

        self.button_previous = QPushButton(self)
        self.button_previous.clicked.connect(self.on_bouton_precedent_click)
        self.button_previous.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_precedent.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_previous.setIcon(QIcon(pixmap))
        self.button_previous.setIconSize(pixmap.rect().size())
        self.button_previous.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_previous)

        self.button_play = QPushButton(self)
        self.button_play.clicked.connect(self.on_bouton_lecture_click)
        self.button_play.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_play.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_play.setIcon(QIcon(pixmap))
        self.button_play.setIconSize(pixmap.rect().size())
        self.button_play.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_play)

        self.button_next = QPushButton(self)
        self.button_next.clicked.connect(self.on_bouton_suivant_click)
        self.button_next.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_suivant.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_next.setIcon(QIcon(pixmap))
        self.button_next.setIconSize(pixmap.rect().size())
        self.button_next.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_next)

        self.button_refresh = QPushButton(self)
        self.button_refresh.clicked.connect(self.on_bouton_refresh_clicked)
        self.button_refresh.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_refresh.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_refresh.setIcon(QIcon(pixmap))
        self.button_refresh.setIconSize(pixmap.rect().size())
        self.button_refresh.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_refresh)

        self.button_reseau = QPushButton(self)
        self.button_reseau.clicked.connect(self.on_bouton_reseau_clicked)
        self.button_reseau.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_reseau_nope.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_reseau.setIcon(QIcon(pixmap))
        self.button_reseau.setIconSize(pixmap.rect().size())
        self.button_reseau.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_reseau)

        self.button_vu = QPushButton(self)
        self.button_vu.clicked.connect(self.on_bouton_vu_clicked)
        self.button_vu.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_vu.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_vu.setIcon(QIcon(pixmap))
        self.button_vu.setIconSize(pixmap.rect().size())
        self.button_vu.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_vu)

        self.button_erreur = QPushButton(self)
        self.button_erreur.clicked.connect(self.on_bouton_erreur_clicked)
        self.button_erreur.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_erreur.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_erreur.setIcon(QIcon(pixmap))
        self.button_erreur.setIconSize(pixmap.rect().size())
        self.button_erreur.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_erreur)

        self.button_quit = QPushButton(self)
        self.button_quit.clicked.connect(self.quit)
        self.button_quit.setFixedHeight(button_height)
        path_p = "data\\ressources\\bouton_quitter.png"
        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(button_height)
        self.button_quit.setIcon(QIcon(pixmap))
        self.button_quit.setIconSize(pixmap.rect().size())
        self.button_quit.setFixedSize(pixmap.rect().size())
        layout_button.addWidget(self.button_quit)

        layout_droit.addLayout(layout_button)

        layout = QHBoxLayout()
        layout.addLayout(layout_gauche)
        layout.addLayout(layout_droit)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.update_HUD()

        self.show()

    def draw_widget_note(self, *args):
        font_txt = QFont("Times", 16)

        #print("draw frise")
        qp = self.painter
        qp.begin(self.widget_note)

        width = self.widget_note.width()
        height = self.widget_note.height()

        color = QColor(255, 255, 255)
        qp.setBrush(color)
        qp.setPen(Qt.darkGray)
        qp.drawRect(0, 0, width-1, height-1)

        #draw les nétoiles
        r_ext = height/2-3
        r_int = r_ext/2
        phase = -np.pi/2

        r, g, b = colormap(self.current_note / 10.0)
        qp.setBrush(QColor(r, g, b))
        note = np.round(self.current_note)
        for j in range(5):
            x = int(r_ext) + 3 + j*2*(int(r_ext)+3)
            y = int(r_ext) + 3
            points = []
            for i in range(5):
                X = x + int(r_ext*np.cos(2*i*np.pi/5.0 + phase))
                Y = y + int(r_ext*np.sin(2*i*np.pi/5.0 + phase))
                points.append(QPoint(X, Y))
                X = x + int(r_int*np.cos(2*i*np.pi/5.0 + phase + np.pi/5))
                Y = y + int(r_int*np.sin(2*i*np.pi/5.0 + phase + np.pi/5))
                points.append(QPoint(X, Y))

            if(2*j-note+2 == 1):
                #on coupe l'étoile en 2
                points_droit = points[:len(points)//2+1] #+ [points[-1]]
                points_gauche = points[len(points)//2:] + [points[0]]

                qp.setBrush(QColor(r, g, b))
                poly = QPolygon(points_gauche)
                qp.drawPolygon(poly)


                qp.setBrush(QColor(255, 255, 255))
                poly = QPolygon(points_droit)
                qp.drawPolygon(poly)
            elif (2*j >= note):
                qp.setBrush(QColor(255, 255, 255))
                poly = QPolygon(points)
                qp.drawPolygon(poly)
            else :
                qp.setBrush(QColor(r, g, b))
                poly = QPolygon(points)
                qp.drawPolygon(poly)

        qp.setFont(font_txt)
        qp.drawText(int(width*3/5.0), int(height/2+7), "(" + str(self.current_note) + "/10)")

        qp.end()

    def draw_widget_affiche(self, *args):
        qp = self.painter
        qp.begin(self.widget_affiches)

        width = self.widget_affiches.width()
        height = self.widget_affiches.height()

        color = QColor(250, 250, 250)
        qp.setBrush(color)
        qp.setPen(Qt.darkGray)
        qp.drawRect(120, 0, width - 1 - 120*2, height - 1)
        qp.end()

    def updateFanart(self):
        try :
            titre = reecriture(self.main.selection_films[self.main.film_selected, 0]).lower()
            annee = self.main.selection_films[self.main.film_selected, 1]
            path_p = "data\\fanart\\" + str(titre) + " " + str(annee) + ".jpg"

            pixmap = QPixmap(path_p)
        except :
            pixmap = QPixmap()

        pixmap = pixmap.scaledToHeight(480)
        #self.label_fanart.setFixedSize(pixmap.size())
        self.label_fanart.setPixmap(pixmap)

    def update_logo_qualite(self):
        qualite = self.main.selection_films[self.main.film_selected, 5]

        if(qualite == "1080p"):
            path_p = "data\\ressources\\logo_1080p.png"
        elif(qualite == "720p"):
            path_p = "data\\ressources\\logo_720p.png"
        elif("dvd" in qualite.lower()):
            path_p = "data\\ressources\\logo_DVD.png"
        elif ("hd" in qualite.lower() or "bd" in qualite.lower()):
            path_p = "data\\ressources\\logo_HD.png"
        else:
            print("qualité non reconnue : ", qualite)
            path_p = "data\\ressources\\logo_HD.png"

        pixmap = QPixmap(path_p)
        pixmap = pixmap.scaledToHeight(60)
        self.label_logo_qualite.setPixmap(pixmap)

    def updateAffiche(self):
        n = len(self.l_affiche)
        for i in range(-n//2, n//2+1):
            try :
                j = (self.main.film_selected+i)%self.main.selection_films.shape[0]
                titre = reecriture(self.main.selection_films[j, 0]).lower()
                annee = self.main.selection_films[j, 1]
                path_p = "data\\poster\\" + str(titre) + " " + str(annee) + ".jpg"

                pixmap = QPixmap(path_p)
            except :
                pixmap = QPixmap()
                print("buggy bug")

            pixmap = pixmap.scaledToHeight(300 - 30*abs(i))
            #print(pixmap.size())
            #self.label_affiche.setFixedSize(pixmap.size())
            #self.label_affiche.setPixmap(pixmap)

            self.l_affiche[i + n//2].setPixmap(pixmap)

    def update_HUD(self):

        #récupération des informations
        titre = reecriture(self.main.selection_films[self.main.film_selected, 0]).lower()
        annee = self.main.selection_films[self.main.film_selected, 1]
        titre_vrai, original_title, collection, date, categories, synopsis, realisateurs, acteurs, note, VO, pays, adult = bdd.get_entry(titre, annee)

        #print("affichage du film n°", self.main.film_selected)
        #print(titre, annee)

        qualite = self.main.selection_films[self.main.film_selected, 5]
        langue = self.main.selection_films[self.main.film_selected, 4]

        self.current_note = note

        s = ""
        for cat in categories:
            s += cat + ", "
        genre =  s[:-2]

        s = ""
        n = 0
        for real in realisateurs:
            s += real + ", "
            n+=1
            if(n > 1):
                break
        real =  s[:-2]

        s = ""
        n = 0
        for act in acteurs:
            s += act[0] + " (" + act[1] + "), "
            n+=1
            if(n > 4):
                #on affiche que 5 acteurs, sinon ça surcharge l'affichage
                break
        act =  s[:-2]

        s = ""
        for p in pays:
            p = traduire_pays(p)
            s += p + ", "
        pays = s[:-2]

        #durée
        time = None
        
        try:
            path_film = self.main.selection_films[self.main.film_selected, 7]
            with open(path_film, 'rb') as f:
                mkv = enzyme.MKV(f)
            if (mkv.info != None):
                time = mkv.info.duration
        except NameError:
            pass
        except enzyme.MalformedMKVError as e:
            print(titre, e)

        if(time != None):
            time = str(time).split('.')[0]
            time = time.split(":")
            heure = time[0]
            minutes = time[1]
        else :
            heure = 0
            minutes = 0

        txt = '<h1><span style="color: #9c27b0; text-align: center;">' + titre_vrai + '<\span>'
        txt += ' <span style="color: #000000;">- ' + date[:4] + '</span></h1>'

        self.label_titre_annee.setText(txt)

        txt_gauche = '<h3><span style="color: #0000ff;">Acteurs :</span></h3>'
        txt_gauche += '<p>' + act + '</p>'
        txt_gauche += '<h3><span style="color: #0000ff;">Genre :</span></h3>'
        txt_gauche += '<p>' + genre + '</p>'
        txt_gauche += '<h3><span style="color: #0000ff;">Dur&eacute;e :</span></h3>'
        txt_gauche += '<p>' + str(heure) + 'h ' + str(minutes) + 'min</p>'

        self.label_description_gauche.setText(txt_gauche)

        txt_droit = '<h3><span style="color: #0000ff;">R&eacute;alisateurs :</span></h3>'
        txt_droit += '<p>' + real + '</p>'
        txt_droit += '<h3><span style="color: #0000ff;">Langue :</span></h3>'
        txt_droit += '<p>' + langue + '</p>'
        txt_droit += '<h3><span style="color: #0000ff;">Pays :</span></h3>'
        txt_droit += '<p>' + str(pays) + '</p>'

        self.label_description_droit.setText(txt_droit)

        txt_syno = '<p><strong>Synopsis : </strong></p>'
        txt_syno += '<p>' + synopsis + '</p><hr />'

        self.label_synopsis.setText(txt_syno)


        self.updateFanart()
        self.updateAffiche()
        self.update_logo_qualite()
        self.widget_note.repaint()
        self.widget_affiches.repaint()

    def updateTableWidget(self, selection_films):
        self.tableWidget.setRowCount(selection_films.shape[0])
        for i in range(selection_films.shape[0]):
            item = QTableWidgetItem(selection_films[i,0])
            self.tableWidget.setItem(i, 0, item)

    @pyqtSlot()
    def on_random_clicked(self):
        print("Random clicked")
        r = np.random.randint(0, self.main.selection_films.shape[0])
        self.main.film_selected = r
        self.tableWidget.setCurrentCell(r, 0)
        self.update_HUD()

    @pyqtSlot()
    def on_zone_recherche_text_changed(self):
        if(self.zoneRecherche.text() == "Recherche..."):
            pass
        if(self.zoneRecherche.text() == "Recherche.."):
            self.zoneRecherche.setText("")
        elif(self.zoneRecherche.text() != "" ):
            self.main.update_selection(self.zoneRecherche.text())
            self.updateTableWidget(self.main.selection_films)
            self.main.film_selected = 0
            self.tableWidget.setCurrentCell(0, 0)
            self.update_HUD()

        elif(len(self.zoneRecherche.text()) == 0):
            self.main.Kword = ""
            self.main.update_selection()
            self.updateTableWidget(self.main.selection_films)
            self.main.film_selected = 0
            self.tableWidget.setCurrentCell(0, 0)
            self.update_HUD()

    @pyqtSlot()
    def on_table_double_click(self):
        self.main.film_selected = self.tableWidget.selectedItems()[0].row()
        self.update_HUD()

    @pyqtSlot()
    def on_table_click(self):
        self.main.film_selected = self.tableWidget.selectedItems()[0].row()
        self.update_HUD()

    @pyqtSlot()
    def on_item_selection_changed(self):
        self.main.film_selected = self.tableWidget.currentRow()
        self.update_HUD()

    @pyqtSlot()
    def on_bouton_precedent_click(self):
        film = (self.main.film_selected-1)%self.main.selection_films.shape[0]
        self.main.film_selected = film
        self.tableWidget.setCurrentCell(film, 0)
        self.update_HUD()

    @pyqtSlot()
    def on_bouton_lecture_click(self):
        print("Lecture : " + self.main.selection_films[self.main.film_selected, 7] + "|")
        sp.Popen(("C:\Program Files\VideoLAN\VLC\\vlc", self.main.selection_films[self.main.film_selected, 7])) #"F:\\" +

    @pyqtSlot()
    def on_bouton_suivant_click(self):
        film = (self.main.film_selected+1)%self.main.selection_films.shape[0]
        self.main.film_selected = film
        self.tableWidget.setCurrentCell(film, 0)
        self.update_HUD()

    def pile_add(self, obj):
        if(len(self.popup_pile) >0):
            self.popup_pile[-1].hide()
        self.popup_pile.append(obj)
        self.popup_pile[-1].show()

    def pile_remove(self):
        popup = self.popup_pile.pop(-1)
        popup.hide_popup()
        if(len(self.popup_pile) > 0):
            self.popup_pile[-1].show()

    def on_escape_key_pressed(self):
        # on joue avec la pile
        # si elle est vide on ouvre le premier popup
        if (len(self.popup_pile) == 0):
            self.pile_add(self.popup_escape)
        else:
            self.pile_remove()

    def on_bouton_refresh_clicked(self):
        self.main.update_sources()
        self.update_HUD()
        self.updateTableWidget(self.main.films)

    def on_bouton_reseau_clicked(self):
        self.main.should_search_upnp = not(self.main.should_search_upnp)

        button_height = 40

        if(self.main.should_search_upnp):
            path_p = "data\\ressources\\bouton_reseau.png"
            pixmap = QPixmap(path_p)
            pixmap = pixmap.scaledToHeight(button_height)
            self.button_reseau.setIcon(QIcon(pixmap))
        else:
            path_p = "data\\ressources\\bouton_reseau_nope.png"
            pixmap = QPixmap(path_p)
            pixmap = pixmap.scaledToHeight(button_height)
            self.button_reseau.setIcon(QIcon(pixmap))

        self.main.update_sources()
        self.update_HUD()
        self.updateTableWidget(self.main.films)

    def on_bouton_vu_clicked(self):
        self.main.update_sources()
        self.update_HUD()
        self.updateTableWidget(self.main.films)

    def on_bouton_erreur_clicked(self):
        """
        on ecrit dans le fichier film_erreur que ce film a un problème
        """
        print("Problème avec le film : ", self.main.selection_films[self.main.film_selected, 0], self.main.selection_films[self.main.film_selected, 1])

        f = open("data\\film_erreur.csv", 'a')
        titre = reecriture(self.main.selection_films[self.main.film_selected, 0]).lower()
        annee = self.main.selection_films[self.main.film_selected, 1]
        f.write(titre + ";" + str(annee) + "\n")
        f.close()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.on_escape_key_pressed()

        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Shift:
            self.quit()

        if event.key() == Qt.Key_Space:
            self.on_bouton_lecture_click()

        if(event.key() == Qt.Key_Down or event.key() == Qt.Key_Right):
            self.on_bouton_suivant_click()
        if(event.key() == Qt.Key_Up or event.key() == Qt.Key_Left):
            self.on_bouton_precedent_click()

        if(event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return or event.key() == Qt.Key_Execute):
            self.on_bouton_lecture_click()

        if(event.key() == Qt.Key_R):
            self.on_random_clicked()

    def quit(self):
        print("\nFermeture de QueQuor, à bientôt :)")
        bdd.close()
        self.close()

    def mousePressEvent(self, event):
        if (event.button() == Qt.MiddleButton):
            #c'est le bouton de la molette, donc film alèatoire
            self.on_random_clicked()
        if(event.button() == Qt.ForwardButton):
            self.on_bouton_suivant_click()

    def wheelEvent(self, event):
        print("salut")
        numDegrees = event.angleDelta().y()  / 8.0
        numSteps = numDegrees / 15.0

        if(numSteps > 0):
            self.on_bouton_suivant_click()
        else:
            self.on_bouton_precedent_click()
        event.accept()


StyleSheet = '''
QPushButton {
    border: none;
}
#ButtonPrev {
    background-color: #9c27b0;
    border-radius: 5px;       
}
#ButtonPrev:hover {
    background-color: #da5cff;
    color: #fff;              
}
#ButtonPrev:pressed {
    background-color: #ffc9e4;
}
#ButtonNext {
    background-color: #9c27b0;
    border-radius: 5px;       
}
#ButtonNext:hover {
    background-color: #da5cff;
    color: #fff;              
}
#ButtonNext:pressed {
    background-color: #ffc9e4;
}
#ButtonPlay {
    background-color: #2196f3;
    min-width:  104px;
    max-width:  104px;
    min-height: 104px;
    max-height: 104px;
    border-radius: 52px;        
}
#ButtonPlay:hover {
    background-color: #64b5f6;
}
#ButtonPlay:pressed {
    background-color: #bbdefb;
}
'''

if __name__ == '__main__':
    #probleme de spam console par enzyme
    import logging
    logging.getLogger("enzyme").setLevel(logging.CRITICAL)

    main = Main()