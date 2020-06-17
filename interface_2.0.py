import sys
from PyQt5.QtWidgets import QDesktopWidget, QStyle, QComboBox, QStyleOptionButton, QProxyStyle, QLineEdit, QAbstractItemView, QLabel, qApp, QStyleFactory, QMainWindow, QPushButton, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QGridLayout, QTextEdit
from PyQt5.QtGui import QIcon, QTextDocument, QFont, QPixmap, QColor, QImage, QPainter, QPalette, QPainterPath, QBrush, QPen, QPolygon
from PyQt5.QtCore import pyqtSlot, QSize, Qt, QPoint, QRect
import numpy as np
import time
import os
import subprocess as sp

import scan
from util import reecriture
import util_bdd as bdd
import util_tmdb

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
        films = np.array(scan.scan_all_films())
        films = films[films[:, 0].argsort()]
        self.films = films[films[:, 3].argsort(kind='mergesort')]

        self.film_selected = 0

        self.selection_films = self.films
        self.categories_selected = []
        self.Kword = ""

        #création de la bdd
        self.bdd = bdd.connect()

        #création de la fenêtre
        app = QApplication(sys.argv)
        app.setStyle(QStyleFactory.create('Fusion'))

        ex = App(self)

        sys.exit(app.exec_())
        bdd.close()

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

            if(film_ok):
                selection.append(film)

        #si aucun film ne match la recherche, on met un film vide
        if(len(selection) == 0):
            selection.append(["Aucun film Trouvé", " ", " ", " ", " ", " ", " ", " ",
                     " ", " ", " ", [], " ", [], [], " ", " "])

        self.selection_films = np.array(selection, dtype=object)

class App(QMainWindow):

    def __init__(self, main):
        super().__init__()
        self.main = main
        self.title = "Qu'es-ce qu'on regarde ?"
        desktop = QDesktopWidget()
        print(desktop.width(), desktop.height())

        self.left = 0
        self.top = 29
        self.width = 3*desktop.width()/4
        self.height = desktop.height()-70


        self.categories = bdd.chercher_categories()
        self.categories.sort()

        style = BaseStyle()
        self.setStyle(style)
        self.setWindowTitle(self.title)

        self.initUI()
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMinimumWidth(desktop.width()/2)
        self.setFixedHeight(self.height)
        self.setStyleSheet(StyleSheet)

        self.show()

    def resizeEvent(self, event):
        desktop = QDesktopWidget()

        width = self.size().width()
        height = desktop.height()-70

        self.y_offset = 24 + 5
        self.x_offset = 5
        self.marge = 10
        self.y_bouton = self.height - self.hauteur - self.x_offset - 24
        self.x_bouton = self.x_offset + self.table_width + self.marge

        self.zoneRecherche.move(self.x_offset, self.y_offset)

        self.tableWidget.setFixedHeight(self.height-(self.y_offset + self.zoneRecherche.height() + self.top))
        self.tableWidget.move(self.x_offset, self.y_offset + self.zoneRecherche.height() + self.marge)

        self.affiche.move(self.x_offset+self.table_width+self.marge, self.y_offset)

        self.description.move(self.x_offset+self.table_width+self.marge+self.affiche.width()+self.marge, self.y_offset)

        synop_height = self.height-(self.y_offset + 400 +200 + self.marge)-50
        synop_width = width - (self.x_offset + self.table_width + self.marge ) - self.x_offset
        synop_x_offset = self.x_offset + self.table_width + self.marge
        synop_y_offset = self.y_offset + 400 + self.marge
        self.synop.setFixedHeight(synop_height)
        self.synop.setFixedWidth(synop_width)
        self.synop.move(synop_x_offset, synop_y_offset)

        self.frise_width = synop_width
        self.frise_height = 100
        self.widget_frise.setFixedWidth(self.frise_width)
        self.widget_frise.setFixedHeight(self.frise_height)
        self.widget_frise.move(synop_x_offset, synop_y_offset + synop_height + self.marge)

        self.description.setFixedWidth(width-(self.x_offset+self.table_width+self.marge+self.affiche.width()+self.marge) -self.x_offset)

        self.bouton_suivant.move(self.x_bouton + 2*(width - self.x_bouton)/3 -self.longueur/2, self.y_bouton)
        self.bouton_precedent.move(self.x_bouton + (width - self.x_bouton)/3 -self.longueur/2, self.y_bouton)
        self.bouton_lecture.move(self.x_bouton + (width - self.x_bouton)/2 -48, self.y_bouton-24)

    def initUI(self):
        #creation du menubar
        menu = self.menuBar()
        categoriesMenu = menu.addMenu("Catégories")
        self.main.categories_selected = self.categories
        self.l_categories = []

        for cat in self.categories :
            fichierClickedAction = QAction('&' + cat, self)
            fichierClickedAction.setCheckable(True)
            fichierClickedAction.setChecked(True)
            self.l_categories.append([fichierClickedAction, cat])
            fichierClickedAction.changed.connect(self.on_categories_checked)
            categoriesMenu.addAction(fichierClickedAction)

        randomMenu = menu.addMenu("Film Random")
        randomClicked = QAction("Random", self)
        randomClicked.setShortcut(Qt.Key_R)
        randomClicked.triggered.connect(self.on_random_clicked)
        #randomClicked.changed.connect(self.on_random_clicked)
        randomMenu.addAction(randomClicked)

        self.table_width = 300
            #recherche zone
        self.zoneRecherche = QLineEdit(self)
        self.zoneRecherche.setFixedWidth(self.table_width)
        self.zoneRecherche.setText("Recherche...")
        self.zoneRecherche.textChanged.connect(self.on_zone_recherche_text_changed)

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

            #les labels
        self.affiche = QLabel(self)
        self.updateAffiche()
        self.affiche.setFixedHeight(400)
        self.affiche.setAlignment(Qt.AlignCenter)

        font_desc = QFont("Times", 14)

        self.description = QTextEdit(self)
        self.description.setFont(font_desc)
        self.description.setFixedHeight(400)

        self.synop = QTextEdit(self)
        self.synop.setFont(font_desc)

        self.painter = QPainter()

        self.widget_frise = QWidget(self)
        self.widget_frise.paintEvent = self.draw_frise

        self.update_HUD()

        font = QFont("Times", 18)
        self.hauteur = 60
        self.longueur = 180
        self.bouton_precedent = QPushButton("Film Précédent", self, objectName="ButtonPrev")
        self.bouton_precedent.setFont(font)
        self.bouton_precedent.setFixedHeight(self.hauteur)
        self.bouton_precedent.setFixedWidth(self.longueur)
        self.bouton_precedent.clicked.connect(self.on_bouton_precedent_click)

        self.bouton_lecture = QPushButton("Lire\nle Film", self, objectName="ButtonPlay")
        self.bouton_lecture.setFont(font)
        self.bouton_lecture.clicked.connect(self.on_bouton_lecture_click)

        self.bouton_suivant = QPushButton("Film Suivant", self, objectName="ButtonNext")
        self.bouton_suivant.setFont(font)
        self.bouton_suivant.setFixedHeight(self.hauteur)
        self.bouton_suivant.setFixedWidth(self.longueur)
        self.bouton_suivant.clicked.connect(self.on_bouton_suivant_click)

        self.show()

    def draw_frise(self, *args):
        #print("draw frise")
        qp = self.painter
        qp.begin(self.widget_frise)
        n = len(self.frise)
        for i in range(n) :
            r, g, b = eval(self.frise[i])
            color = QColor(r, g, b)
            qp.setBrush(color)
            qp.setPen(color)
            qp.drawRect(i*self.frise_width/n, 0, self.frise_width/n+2, self.frise_height-1)
        qp.end()

    def updateAffiche(self):
        try :
            titre = reecriture(self.main.selection_films[self.main.film_selected, 0]).lower()
            annee = self.main.selection_films[self.main.film_selected, 1]
            path_p = "data\\poster\\" + str(titre) + " " + str(annee) + ".jpg"

            pixmap = QPixmap(path_p)
        except :
            pixmap = QPixmap()

        pixmap = pixmap.scaledToHeight(400)
        self.affiche.setFixedSize(pixmap.size())
        self.affiche.setPixmap(pixmap)

    def update_HUD(self):
        f = str("data\\frises\\"+self.main.selection_films[self.main.film_selected, 0])+".csv"
        #f = "data\\frises\\films.csv"
        duree = "0"
        try :
            data = np.loadtxt(f, delimiter=";", dtype=object, encoding='utf-8')
            self.frise = data[1:]
            duree = data[0]
        except OSError as er:
            #print(er)
            #print("Pas de frise pour : ", self.main.selection_films[self.main.film_selected, 0])
            self.frise = ["[150, 150, 150]", "[150, 150, 150]"]

        self.widget_frise.repaint()

        #récupération des informations
        titre = reecriture(self.main.selection_films[self.main.film_selected, 0]).lower()
        annee = self.main.selection_films[self.main.film_selected, 1]
        titre_vrai, original_title, collection, date, categories, synopsis, realisateurs, acteurs, note, VO, pays, adult = bdd.get_entry(titre, annee)

        qualite = self.main.selection_films[self.main.film_selected, 5]
        langue = self.main.selection_films[self.main.film_selected, 4]

        s = ""
        for cat in categories:
            s += cat + ", "
        genre =  s[:-2]

        s = ""
        for real in realisateurs:
            s += real + ", "
        real =  s[:-2]

        s = ""
        for act in acteurs:
            s += act[0] + " (" + act[1] + "), "
        act =  s[:-2]

        #duree = " "
        txt = '<h1 style="color: #9c27b0; text-align: center;">' + titre_vrai + '</h1>'
        txt += '<h3 style="color: #2196f3; text-align: center;">' + date[:4] + "</h3>"
        txt += '<hr/>'
        txt += '<p style="text-align: left;"><span style="color: #99ccff;">De : </span>' + real + '</p>'
        txt += '<p style="text-align: left;"><span style="color: #99ccff;">Avec : </span>' + act + '</p>'
        txt += '<p style="text-align: left;"><span style="color: #99ccff;">Genre : </span>' + genre + '</p>'
        txt += '<hr/>'
        txt+='<p style="text-align: left;"><span style="color: #99ccff;">Dur&eacute;e : </span></span>' + duree + '</p>'
        txt += '<p style="text-align: left;"><span style="color: #99ccff;">Qualit&eacute; : </span>' + qualite + '</p>'
        txt += '<p style="text-align: left;"><span style="color: #99ccff;">Langue : </span>' + langue + '</p>'

        syno = '<p><strong>Synopsis : </strong></p>'
        syno += '<p>' + synopsis + '</p><hr />'

        self.synop.setText(syno)
        self.description.setText(txt)
        self.updateAffiche()

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
    def on_categories_checked(self):
        self.main.categories_selected = []
        for c in self.l_categories :
            if(c[0].isChecked()):
                self.main.categories_selected.append(c[1])
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass
        if event.key() == Qt.Key_Space:
            pass
        if event.key() == Qt.Key_Left:
            pass
        if(event.key() == Qt.Key_Down):
            self.on_bouton_suivant_click()
        if(event.key() == Qt.Key_Up):
            self.on_bouton_precedent_click()

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
    main = Main()